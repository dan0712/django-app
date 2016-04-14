from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer

from main.models import ClientAccount


class ClientAccountSerializer(ReadOnlyModelSerializer):
    """
    AccountSerializer
    """
    class Meta:
        model = ClientAccount
