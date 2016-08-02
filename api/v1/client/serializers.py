from django.db import transaction
from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import ExternalAsset, ExternalAssetTransfer
from client.models import Client, EmailNotificationPrefs
from notifications.signals import notify

from ..user.serializers import FieldUserSerializer


class ClientSerializer(ReadOnlyModelSerializer):
    user = FieldUserSerializer()

    class Meta:
        model = Client


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
