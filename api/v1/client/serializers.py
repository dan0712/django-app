from django.db import transaction
from rest_framework import serializers

from api.v1.address.serializers import AddressSerializer
from api.v1.advisor.serializers import AdvisorFieldSerializer
from api.v1.serializers import ReadOnlyModelSerializer
from main.models import ExternalAsset, ExternalAssetTransfer
from client.models import Client

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
