from api.v1.serializers import ReadOnlyModelSerializer
from main.models import Advisor


class AdvisorSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = Advisor
        exclude = (
            'user',
            'confirmation_key',
            'letter_of_authority', 'betasmartz_agreement',
        )


