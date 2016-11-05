from rest_framework import serializers
from execution.models import ETNALogin, Result


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('SessionId','UserId')


class LoginSerializer(serializers.ModelSerializer):
    Result = ResultSerializer()

    class Meta:
        model = ETNALogin
        fields = ('ResponseCode', 'Ticket', 'Result')

    def create(self, validated_data):
        result_data = validated_data.pop('Result')
        result = Result.objects.create(**result_data)
        login = ETNALogin.objects.create(Result=result, **validated_data)
        return login
