from rest_framework import viewsets
from rest_framework.decorators import detail_route

from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.views import ApiViewMixin

from main.models import ExternalAsset
from client.models import Client
from support.models import SupportRequest

from . import serializers


class ExternalAssetViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    model = ExternalAsset
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = ExternalAsset.objects.all()
    serializer_class = serializers.ExternalAssetSerializer
    pagination_class = None

    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = serializers.ExternalAssetSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return serializers.ExternalAssetWritableSerializer
        else:
            # Default for get and other requests is the read only serializer
            return serializers.ExternalAssetSerializer

    def get_queryset(self):
        qs = super(ExternalAssetViewSet, self).get_queryset()

        # Only return assets which the user has access to.
        user = SupportRequest.target_user(self.request.user)
        return qs.filter_by_user(user)


class ClientViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Client
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super(ClientViewSet, self).get_queryset()

        # Only return Clients the user has access to.
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)
