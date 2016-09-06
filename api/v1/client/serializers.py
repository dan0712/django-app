from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from api.v1.address.serializers import AddressSerializer
from api.v1.advisor.serializers import AdvisorFieldSerializer
from api.v1.serializers import ReadOnlyModelSerializer
from main.models import ExternalAsset, ExternalAssetTransfer, User
from client.models import Client, EmailInvite
from user.models import SecurityQuestion, SecurityAnswer

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
    class Meta:
        model = Client
        fields = (
            'employment_status', 'income', 'occupation',
            'employer', 'us_citizen', 'public_position_insider',
            'ten_percent_insider', 'associated_to_broker_dealer',
            'tax_file_number', 'provide_tfn', 'civil_status'
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

class ClientUserRegistrationSerializer(serializers.Serializer):
    """
    For POST request to register from an email token
    """
    invite_key = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    question_one_id = serializers.IntegerField()
    question_one_answer = serializers.CharField()
    question_two_id = serializers.IntegerField()
    question_two_answer = serializers.CharField()

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get('email')).exists():
            msg = _('Email is already in use')
            raise exceptions.ValidationError(msg)

        invite_params = {
            'invite_key': attrs.get('invite_key'),
            'email': attrs.get('email'),
        }

        if not attrs.get('question_one_id') or not SecurityQuestion.objects.filter(
            pk=attrs['question_one_id']).exists():
            msg = _('Invalid security question #1 ID')
            raise exceptions.ValidationError(msg)
        self.question_one = SecurityQuestion.objects.get(pk=attrs['question_one_id'])

        if not attrs.get('question_two_id') or not SecurityQuestion.objects.filter(
            pk=attrs['question_two_id']).exists():
            msg = _('Invalid security question #2 ID')
            raise exceptions.ValidationError(msg)
        self.question_two = SecurityQuestion.objects.get(pk=attrs['question_two_id'])

        if not attrs.get('question_one_answer'):
            msg = _('Invalid security question #1 answer')
            raise exceptions.ValidationError(msg)
        if not attrs.get('question_two_answer'):
            msg = _('Invalid security question #2 answer')
            raise exceptions.ValidationError(msg)

        invite_lookup = EmailInvite.objects.filter(**invite_params)

        if not invite_lookup.exists():
            msg = _('Invalid invitation key')
            raise exceptions.ValidationError(msg)

        self.invite = invite_lookup.get()

        if self.invite.status == EmailInvite.STATUS_CREATED:
            msg = _('Unable to accept this invitation, it hasnt been sent yet')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_ACCEPTED:
            msg = _('Unable to accept this invitation, it has already been accepted')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_EXPIRED:
            msg = _('Unable to accept this invitation, it has expired')
            raise exceptions.ValidationError(msg)

        if self.invite.status == EmailInvite.STATUS_COMPLETE:
            msg = _('Unable to accept this invitation, it has already been completed')
            raise exceptions.ValidationError(msg)

        return attrs
