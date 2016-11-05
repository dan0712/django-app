from rest_framework import serializers
from execution.ETNA_api.models import ETNALogin


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETNALogin
        fields = ('ResponseCode',)

    def create(self, validated_data):
        return ETNALogin(**validated_data)
