from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from api.v1.address.serializers import AddressSerializer
from api.v1.advisor.serializers import AdvisorFieldSerializer
from api.v1.serializers import ReadOnlyModelSerializer
from main.models import ExternalAsset, ExternalAssetTransfer, User
from user.models import SecurityQuestion, SecurityAnswer
from client.models import Client, EmailNotificationPrefs, EmailInvite, RiskProfileAnswer, RiskProfileGroup
from notifications.signals import notify
from main import constants

from ..user.serializers import UserFieldSerializer


class ClientSerializer(ReadOnlyModelSerializer):
    user = UserFieldSerializer()
    advisor = AdvisorFieldSerializer()
    residential_address = AddressSerializer()

    class Meta:
        model = Client


class ClientFieldSerializer(ReadOnlyModelSerializer):
    residential_address = AddressSerializer()
    advisor = AdvisorFieldSerializer()

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
    def create(self, validated_data):
        # Default to Personal account type for risk profile group on a brand
        # new client (since they have no accounts yet, we have to assume)
        rpg = RiskProfileGroup.objects.get(account_types__account_type=constants.ACCOUNT_TYPE_PERSONAL)
        validated_data.update({
            'risk_profile_group': rpg
        })
        return (super(ClientUpdateSerializer, self)
                .create(validated_data))
    class Meta:
        model = Client
        fields = (
            'employment_status', 'income', 'occupation',
            'employer', 'us_citizen', 'public_position_insider',
            'ten_percent_insider', 'associated_to_broker_dealer',
            'tax_file_number', 'provide_tfn', 'civil_status',
            'risk_profile_responses'
        )


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
        exclude = ('owner',)


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
    class Meta:
        model = EmailInvite
        fields = (
            'invite_key',
            'status',
        )

class PrivateInvitationSerializer(serializers.ModelSerializer):
    # Includes onboarding data
    # Allows POST for registered users
    class Meta:
        model = EmailInvite
        read_only_fields = ('invite_key', 'status')
        fields = (
            'invite_key',
            'status',
            'onboarding_data',
            'onboarding_file_1'
        )


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
