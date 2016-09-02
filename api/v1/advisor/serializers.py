from api.v1.serializers import ReadOnlyModelSerializer
from api.v1.user.serializers import UserFieldSerializer
from main.models import Advisor


class AdvisorSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Advisor
        exclude = (
            'user',
            'confirmation_key',
            'letter_of_authority',
            'betasmartz_agreement',
        )


class AdvisorFieldSerializer(ReadOnlyModelSerializer):
    user = UserFieldSerializer()

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

