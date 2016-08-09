from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import RetrieveAPIView

from api.v1.views import ApiViewMixin
from main.models import Firm
from .serializers import FirmSerializer


class FirmSingleView(ApiViewMixin, RetrieveAPIView):
    serializer_class = FirmSerializer

    def get_queryset(self):
        user = self.request.user
        fields = ['supervisor', 'advisor', 'authorised_representative']
        for field in fields:
            try:
                return Firm.objects.filter(**{
                    '%ss' % field: getattr(user, field)
                })
            except ObjectDoesNotExist:
                pass

        return self.permission_denied(self.request)
