from rest_framework import serializers

from api.v1.serializers import (NoCreateModelSerializer,
                                NoUpdateModelSerializer,
                                ReadOnlyModelSerializer)
from client.models import ClientAccount


class ClientAccountSerializer(ReadOnlyModelSerializer):
    """
    Read-only ClientAccount Serializer
    """

    class Meta:
        model = ClientAccount


class ClientAccountCreateSerializer(NoUpdateModelSerializer):
    """
    When creating an account via the API, we want the name to be required,
    so enforce it.
    """
    account_name = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = ClientAccount
        fields = (
            'account_type',
            'account_name',
            'primary_owner',
        )

    def create(self, validated_data):
        ps = validated_data['primary_owner'].advisor.default_portfolio_set
        validated_data.update({
            'default_portfolio_set': ps,
        })
        return (super(ClientAccountCreateSerializer, self)
                .create(validated_data))


class ClientAccountUpdateSerializer(NoCreateModelSerializer):
    """
    Updatable ClientAccount Serializer
    """

    class Meta:
        model = ClientAccount
        fields = (
            'account_name',
            'tax_loss_harvesting_status',
        )
