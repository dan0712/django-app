from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer, NoCreateModelSerializer

from main.models import ClientAccount, RiskProfileAnswer


class ClientAccountSerializer(ReadOnlyModelSerializer):
    """
    Read-only ClientAccount Serializer
    """
    class Meta:
        model = ClientAccount


class ClientAccountUpdateSerializer(NoCreateModelSerializer):
    """
    Updatable ClientAccount Serializer
    """
    risk_profile_responses = serializers.PrimaryKeyRelatedField(many=True, queryset=RiskProfileAnswer.objects.all())

    class Meta:
        model = ClientAccount
        fields = (
            'tax_loss_harvesting_status',
            'risk_profile_responses',
        )
