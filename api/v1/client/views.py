from rest_framework import viewsets
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.client.serializers import EmailNotificationsSerializer, \
    PersonalInfoSerializer
from api.v1.permissions import IsClient
from api.v1.views import ApiViewMixin
from client.models import Client
from main.models import ExternalAsset
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
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)


class ClientViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Client
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = serializers.ClientSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return serializers.ClientUpdateSerializer
        else:
            # Default for get and other requests is the read only serializer
            return serializers.ClientSerializer

    def get_queryset(self):
        qs = super(ClientViewSet, self).get_queryset()

        # Only return Clients the user has access to.
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)


class EmailNotificationsView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = EmailNotificationsSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user).notification_prefs


class ProfileView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = PersonalInfoSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user)
