from django.contrib.auth import authenticate, login as auth_login
from rest_framework import viewsets, views
from rest_framework import exceptions, parsers, status

from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response

from api.v1.views import ApiViewMixin

from main.models import ExternalAsset, User
from user.models import SecurityQuestion, SecurityAnswer
from client.models import Client, EmailInvite
from support.models import SupportRequest
from api.v1.user.serializers import UserSerializer, AuthSerializer

from . import serializers

import logging

logger = logging.getLogger('api.v1.client.views')

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

class InvitesView(ApiViewMixin, views.APIView):
    pass

class ClientUserRegisterView(ApiViewMixin, views.APIView):
    """
    Register Client's User from an invite token
    """
    permission_classes = []
    serializer_class = serializers.ClientUserRegistrationSerializer

    def post(self, request):
        serializer = serializers.ClientUserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error('Error accepting invitation: %s'%serializer.errors['non_field_errors'][0])
            return Response({'error': 'invitation not found for this email'}, status=status.HTTP_404_NOT_FOUND)

        if not SecurityQuestion.objects.filter(
                pk=request.data.get('question_one_id')).exists():
            msg = _('Invalid security question')
            raise exceptions.ValidationError(msg)

        if not SecurityQuestion.objects.filter(
                pk=request.data.get('question_two_id')).exists():
            msg = _('Invalid security question')
            raise exceptions.ValidationError(msg)

        invite = serializer.invite

        user_params = {
            'email': invite.email,
            'username': invite.email,
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'password': serializer['password'],
        }
        user = User.objects.create_user(**user_params)

        invite.status = EmailInvite.STATUS_ACCEPTED
        invite.user = user

        invite.save()

        login_params = {
            'email': user.email,
            'password': serializer['password']
        }

        user = authenticate(**login_params)

        # check if user is authenticated
        if not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        # Log the user in with a session as well.
        auth_login(request, user)

        user_serializer = UserSerializer(instance=user)

        return Response(user_serializer.data)

