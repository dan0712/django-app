import logging

from django.db import transaction
from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer
from address.models import Region, Address

REGION_KEY = 'region'

logger = logging.getLogger('api.v1.address.serializers')


class RegionSerializer(serializers.ModelSerializer):
    """
    For GET/POST only
    """
    class Meta:
        model = Region
        fields = (
            'name',
            'code',
            'country',
        )
        # disable the default validators, as they include the unique_together validator, which kills us as we
        # simply reuse if existing.
        validators = []

    def create(self, validated_data):
        region = Region.objects.filter(code=validated_data['code'], country=validated_data['country']).first()
        if region is None:
            region = super(RegionSerializer, self).create(validated_data)
        return region

    def update(self, instance, validated_data):
        raise Exception("Not a valid operation.")


class AddressSerializer(ReadOnlyModelSerializer):
    """
    For Read (GET) requests only
    """
    region = RegionSerializer()

    class Meta:
        model = Address
        exclude = ('id',)


class AddressUpdateSerializer(serializers.ModelSerializer):
    """
    For Update (PUT/POST) requests only
    """
    region = RegionSerializer()

    class Meta:
        model = Address
        fields = (
            'address',
            'post_code',
            REGION_KEY,
            'global_id',
        )

    @transaction.atomic
    def create(self, validated_data):
        region_ser = RegionSerializer(data=validated_data.pop(REGION_KEY))
        region_ser.is_valid(raise_exception=True)
        validated_data[REGION_KEY] = region_ser.save()
        return super(AddressUpdateSerializer, self).create(validated_data)
