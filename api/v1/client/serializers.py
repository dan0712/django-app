from api.v1.serializers import ReadOnlyModelSerializer
from main.models import Client

from ..user.serializers import FieldUserSerializer

__all__ = (
    'ClientSerializer',
)


class ClientSerializer(ReadOnlyModelSerializer):
    user = FieldUserSerializer()

    class Meta:
        model = Client
