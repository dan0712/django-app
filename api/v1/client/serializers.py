from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from api.v1.address.serializers import AddressSerializer, AddressUpdateSerializer
from api.v1.advisor.serializers import AdvisorFieldSerializer
from api.v1.serializers import ReadOnlyModelSerializer
from main.constants import ACCOUNT_TYPE_PERSONAL
from main.models import ExternalAsset, ExternalAssetTransfer, User
from client.models import Client, EmailNotificationPrefs, EmailInvite, RiskProfileAnswer, RiskProfileGroup, \
    AccountTypeRiskProfileGroup
from notifications.signals import notify
from main import constants
from pdf_parsers.tax_return import parse_pdf
from ..user.serializers import UserFieldSerializer, PhoneNumberValidationSerializer
import logging
import uuid

logger = logging.getLogger('api.v1.client.serializers')
RESIDENTIAL_ADDRESS_KEY = 'residential_address'


class ClientSerializer(ReadOnlyModelSerializer):
    user = UserFieldSerializer()
    advisor = AdvisorFieldSerializer()
    residential_address = AddressSerializer()
    regional_data = serializers.JSONField()

    class Meta:
        model = Client


class ClientFieldSerializer(ReadOnlyModelSerializer):
    residential_address = AddressSerializer()
    advisor = AdvisorFieldSerializer()
    regional_data = serializers.JSONField()

    class Meta:
        model = Client
        exclude = (
            'user',
            'client_agreement',
            'confirmation_key',
            'create_date',
        )


class ClientUpdateSerializer(serializers.ModelSerializer):
    """
    Write (POST/PUT) update requests only
    """
    qs = RiskProfileAnswer.objects.all()
    risk_profile_responses = serializers.PrimaryKeyRelatedField(many=True,
                                                                queryset=qs,
                                                                required=False)
    residential_address = AddressUpdateSerializer()
    regional_data = serializers.JSONField()

    class Meta:
        model = Client
        fields = (
            'employment_status',
            RESIDENTIAL_ADDRESS_KEY,
            'income',
            'occupation',
            'employer',
            'civil_status',
            'risk_profile_responses',
            'betasmartz_agreement',
            'advisor_agreement',
            'phone_num',
            'regional_data',
        )

    def validate_phone_num(self, phone_num):
        serializer = PhoneNumberValidationSerializer(data={'number': phone_num})
        if not serializer.is_valid():
            raise serializers.ValidationError('Invalid phone number')
        return serializer.validated_data

    def create(self, validated_data):
        # Default to Personal account type for risk profile group on a brand
        # new client (since they have no accounts yet, we have to assume)
        rpg = RiskProfileGroup.objects.get(account_types__account_type=constants.ACCOUNT_TYPE_PERSONAL)
        validated_data['risk_profile_group'] = rpg

        address_ser = AddressUpdateSerializer(data=validated_data.pop(RESIDENTIAL_ADDRESS_KEY))
        address_ser.is_valid(raise_exception=True)
        validated_data[RESIDENTIAL_ADDRESS_KEY] = address_ser.save()

        # For now we auto confirm and approve the client.
        validated_data['is_confirmed'] = True
        validated_data['is_accepted'] = True

        return super(ClientUpdateSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        add_data = validated_data.pop(RESIDENTIAL_ADDRESS_KEY, None)
        if add_data is not None:
            address_ser = AddressUpdateSerializer(data=add_data)
            address_ser.is_valid(raise_exception=True)
            validated_data[RESIDENTIAL_ADDRESS_KEY] = address_ser.save()

        return super(ClientUpdateSerializer, self).update(instance, validated_data)


class EATransferPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAssetTransfer
        exclude = ('asset',)


class EAWritableTransferPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAssetTransfer
        fields = (
            'begin_date',
            'amount',
            'growth',
            'schedule',
        )


class ExternalAssetSerializer(ReadOnlyModelSerializer):
    transfer_plan = EATransferPlanSerializer()

    class Meta:
        model = ExternalAsset


class ExternalAssetWritableSerializer(serializers.ModelSerializer):
    # For the reverse relation.
    transfer_plan = EAWritableTransferPlanSerializer(required=False)

    class Meta:
        model = ExternalAsset
        fields = (
            'type',
            'name',
            'owner',
            'description',
            'valuation',
            'valuation_date',
            'growth',
            'acquisition_date',
            'debt',
            'transfer_plan',
        )

    def __init__(self, *args, **kwargs):
        super(ExternalAssetWritableSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request.method == 'PUT':
            for field in self.fields.values():
                field.required = False

    @transaction.atomic
    def update(self, instance, validated_data):
        txp = validated_data.pop('transfer_plan', None)
        if txp:
            if instance.transfer_plan is not None:
                instance.transfer_plan.delete()
            ser = EAWritableTransferPlanSerializer(data=txp)
            ser.is_valid(raise_exception=True)
            ser.save(asset=instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        txp = validated_data.pop('transfer_plan', None)
        instance = ExternalAsset.objects.create(**validated_data)
        if txp:
            ser = EAWritableTransferPlanSerializer(data=txp)
            ser.is_valid(raise_exception=True)
            ser.save(asset=instance)
        return instance


class InvitationSerializer(ReadOnlyModelSerializer):
    """
    A user in the middle of onboarding will use this
    serializer, pre-registration and non-authenticated
    """
    firm_name = serializers.SerializerMethodField()
    firm_logo = serializers.SerializerMethodField()
    firm_colored_logo = serializers.SerializerMethodField()

    class Meta:
        model = EmailInvite
        fields = (
            'invite_key',
            'status',
            'first_name',
            'middle_name',
            'last_name',
            'reason',
            'advisor',
            'firm_name',
            'firm_logo',
            'firm_colored_logo',
        )

    def get_firm_name(self, obj):
        return obj.advisor.firm.name

    def get_firm_logo(self, obj):
        return obj.advisor.firm.white_logo

    def get_firm_colored_logo(self, obj):
        return obj.advisor.firm.colored_logo


class PrivateInvitationSerializer(serializers.ModelSerializer):
    """
    Authenticated users will retrieve and update through this
    serializer.
    """
    # Includes onboarding data
    # Allows POST for registered users
    onboarding_data = serializers.JSONField()
    risk_profile_group = serializers.SerializerMethodField()
    firm_name = serializers.SerializerMethodField()
    firm_logo = serializers.SerializerMethodField()
    firm_colored_logo = serializers.SerializerMethodField()
    tax_transcript_data = serializers.SerializerMethodField()

    class Meta:
        model = EmailInvite
        read_only_fields = ('invite_key', 'status')
        fields = (
            'invite_key',
            'status',
            'onboarding_data',
            'risk_profile_group',
            'reason',
            'advisor',
            'firm_name',
            'firm_logo',
            'firm_colored_logo',
            'tax_transcript',
            'tax_transcript_data',  # this will be stored to client.region_data.tax_transcript_data
        )

    def get_risk_profile_group(self, obj):
        return AccountTypeRiskProfileGroup.objects.get(account_type=ACCOUNT_TYPE_PERSONAL).id

    def get_firm_name(self, obj):
        return obj.advisor.firm.name

    def get_firm_logo(self, obj):
        return obj.advisor.firm.white_logo

    def get_firm_colored_logo(self, obj):
        return obj.advisor.firm.colored_logo

    def get_tax_transcript_data(self, obj):
        # parse_pdf
        if obj.tax_transcript:
            # save to tmp file to pass to parse_pdf
            # TODO: parse_pdf using subprocess file status command
            # to detect pdf_fonts, need to replace that with
            # something we can pass the in-memory file data here
            tmp_filename = '/tmp/' + str(uuid.uuid4()) + '.pdf'
            with open(tmp_filename, 'wb+') as f:
                for chunk in obj.tax_transcript.chunks():
                    f.write(chunk)
            obj.tax_transcript_data = parse_pdf(tmp_filename)
            return obj.tax_transcript_data
        return None


class ClientUserRegistrationSerializer(serializers.Serializer):
    """
    For POST request to register from an email token
    """
    invite_key = serializers.CharField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})
    question_one = serializers.CharField(required=True)
    question_one_answer = serializers.CharField(required=True)
    question_two = serializers.CharField(required=True)
    question_two_answer = serializers.CharField(required=True)

    def validate(self, attrs):
        invite_params = {
            'invite_key': attrs.get('invite_key'),
        }

        invite_lookup = EmailInvite.objects.filter(**invite_params)

        if not invite_lookup.exists():
            msg = _('Invalid invitation key')
            raise exceptions.ValidationError(msg)

        self.invite = invite_lookup.get()

        if User.objects.filter(email=self.invite.email).exists():
            msg = _('Email is already in use')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_CREATED:
            msg = _('Unable to accept this invitation, it hasnt been sent yet')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_ACCEPTED:
            msg = _('Unable to accept this invitation, it has already been accepted')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_EXPIRED:
            self.invite.advisor.user.email_user('A client tried to use an expired invitation'
                    "Your client %s %s (%s) just tried to register using an invite "
                    "you sent them, but it has expired!"%
                    (self.invite.first_name, self.invite.last_name, self.invite.email))
            msg = _('Unable to accept this invitation, it has expired')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_COMPLETE:
            msg = _('Unable to accept this invitation, it has already been completed')
            raise exceptions.ValidationError(msg)

        return attrs


class EmailNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotificationPrefs
        exclude = 'id', 'client',


class PersonalInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    address = serializers.CharField(source='residential_address.address', required=False)
    phone = serializers.CharField(source='phone_num', required=False)

    class Meta:
        model = Client
        fields = ('first_name', 'middle_name', 'last_name', 'address',
                  'phone', 'employment_status', 'occupation', 'employer',
                  'income', 'net_worth')

    def save(self, **kwargs):
        new_address = self.validated_data.pop('residential_address', None)
        client = self.instance # client.Client
        if new_address:
            current_address = client.residential_address
            current_address.address = new_address['address']
            current_address.save(update_fields=['address'])
        instance = super(PersonalInfoSerializer, self).save(**kwargs)

        notify.send(client.advisor.user, recipient=client.user,
                    verb='update-personal-info')

        # TODO generate a new SOA

        return instance
