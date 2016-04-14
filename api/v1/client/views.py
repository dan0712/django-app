from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.views import ApiViewMixin

from main.models import Client

from . import serializers


class ClientViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Client
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super(ClientViewSet, self).get_queryset()

        # show "permissioned" records only
        user = self.request.user
        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)
        elif user.is_client:
            qs = qs.filter_by_client(user.client)
        else:
            raise PermissionDenied('Only Advisors or Clients are allowed to access clients.')

        return qs
