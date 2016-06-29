from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer, NoCreateModelSerializer, NoUpdateModelSerializer

from main.models import ClientAccount, RiskProfileAnswer, RiskProfileGroup, ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_JOINT


class ClientAccountSerializer(ReadOnlyModelSerializer):
    """
    Read-only ClientAccount Serializer
    """
    class Meta:
        model = ClientAccount


class ClientAccountCreateSerializer(NoUpdateModelSerializer):
    # When creating an account via the API, we want the name to be required, so enforce it.
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
        rpg = RiskProfileGroup.objects.get(account_types__account_type=validated_data['account_type'])
        validated_data.update({
            'default_portfolio_set': ps,
            'risk_profile_group': rpg
        })
        return super(ClientAccountCreateSerializer, self).create(validated_data)


class ClientAccountUpdateSerializer(NoCreateModelSerializer):
    """
    Updatable ClientAccount Serializer
    """
    risk_profile_responses = serializers.PrimaryKeyRelatedField(many=True,
                                                                queryset=RiskProfileAnswer.objects.all(),
                                                                required=False)

    class Meta:
        model = ClientAccount
        fields = (
            'account_name',
            'tax_loss_harvesting_status',
            'risk_profile_responses',
        )
