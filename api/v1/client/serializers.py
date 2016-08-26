from django.db import transaction
from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import ExternalAsset, ExternalAssetTransfer, Advisor, User
from client.models import Client

from ..user.serializers import UserFieldSerializer


class ClientAdvisorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'prepopulated',
            'is_staff', 'is_superuser',
            'password', 'last_login',
            'user_permissions', 'groups',
            'username', 'email',
            'date_joined',
            'is_active',
        )


class ClientAdvisorSerializer(serializers.ModelSerializer):
    user = ClientAdvisorUserSerializer()

    class Meta:
        model = Advisor
        fields = (
            'id',
            'gender',
            'work_phone_num',
            'user',
            'firm',
            'email'
        )


class ClientSerializer(ReadOnlyModelSerializer):
    user = UserFieldSerializer()
    advisor = serializers.SerializerMethodField()

    class Meta:
        model = Client

    def get_advisor(self, client):
        return ClientAdvisorSerializer(client.advisor).data


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
