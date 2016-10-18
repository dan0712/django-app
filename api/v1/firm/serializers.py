from api.v1.serializers import ReadOnlyModelSerializer
from main.models import Firm


class FirmSerializer(ReadOnlyModelSerializer):

    class Meta:
        model = Firm
        fields = (
            'id',
            'logo',
            'colored_logo',
            'name',
            'slug',
        )
