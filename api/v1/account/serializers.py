from rest_framework import serializers

from api.v1.serializers import (NoCreateModelSerializer,
                                NoUpdateModelSerializer,
                                ReadOnlyModelSerializer)
from client.models import ClientAccount, RiskProfileAnswer, RiskProfileGroup


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
        ac_type = validated_data['account_type']
        rpg = RiskProfileGroup.objects.get(account_types__account_type=ac_type)
        validated_data.update({
            'default_portfolio_set': ps,
            'risk_profile_group': rpg,
        })
        return (super(ClientAccountCreateSerializer, self)
                .create(validated_data))


class ClientAccountUpdateSerializer(NoCreateModelSerializer):
    """
    Updatable ClientAccount Serializer
    """
    qs = RiskProfileAnswer.objects.all()
    risk_profile_responses = serializers.PrimaryKeyRelatedField(many=True,
                                                                queryset=qs,
                                                                required=False)

    class Meta:
        model = ClientAccount
        fields = (
            'account_name',
            'tax_loss_harvesting_status',
            'risk_profile_responses',
        )
