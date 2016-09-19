from django.contrib.auth import authenticate, login as auth_login
from rest_framework import viewsets, views
from rest_framework import exceptions, parsers, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response

from api.v1.client.serializers import EmailNotificationsSerializer, \
    PersonalInfoSerializer
from api.v1.permissions import IsClient
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

    def post(self, request):
        if EmailInvite.STATUS_ACCEPTED == getattr(
            self.request.user.invitation, 'status', None):
            # Email the user "Welcome Aboard"
            self.request.user.email_user('Welcome to BetaSmartz!',
                    "Congratulations! You've setup your first account, "
                    "you're ready to start using BetaSmartz!")
            return super(ClientViewSet, self).post(request)
        return Response({'error': 'requires account with accepted invitation'},
                        status=HTTP_405_METHOD_NOT_ALLOWED)



class InvitesView(ApiViewMixin, views.APIView):
    permission_classes = []
    serializer_class = serializers.PrivateInvitationSerializer
    parser_classes = (
        parsers.JSONParser, parsers.FileUploadParser, parsers.MultiPartParser,
    )
    def get(self, request, invite_key):
        find_invite = EmailInvite.objects.filter(invite_key=invite_key)
        if not find_invite.exists:
            return Response({'error': 'invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        invite = find_invite.get()

        if not request.user.is_authenticated():
            data = serializers.InvitationSerializer(instance=invite).data
        else:
            data = self.serializer_class(instance=invite).data
        return Response(data)

    def put(self, request, invite_key):
        find_invite = EmailInvite.objects.filter(invite_key=invite_key)
        if not find_invite.exists:
            return Response({'error': 'invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        invite = find_invite.get()

        if not request.user.is_authenticated():
            return Response({'error': 'not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        if invite.status == EmailInvite.STATUS_EXPIRED:
            invite.advisor.user.email_user('A client tried to use an expired invitation'
                    "Your client %s %s (%s) just tried to register using an invite "
                    "you sent them, but it has expired!"%
                    (client.first_name, client.last_name, client.email))

        if invite.status != EmailInvite.STATUS_ACCEPTED:
            return Response(serializers.InvitationSerializer(invite).data,
                            status=status.HTTP_304_NOT_MODIFIED)

        serializer = self.serializer_class(invite, data=request.data,
                                           partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializers.InvitationSerializer(invite).data)


class ClientUserRegisterView(ApiViewMixin, views.APIView):
    """
    Register Client's User from an invite token
    """
    permission_classes = []
    serializer_class = serializers.ClientUserRegistrationSerializer

    def post(self, request):
        serializer = serializers.ClientUserRegistrationSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            logger.error('Error accepting invitation: %s'%serializer.errors['non_field_errors'][0])
            return Response({'error': 'invitation not found for this email'}, status=status.HTTP_404_NOT_FOUND)
        invite = serializer.invite

        user_params = {
            'email': invite.email,
            'username': invite.email,
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'password': serializer.validated_data['password'],
        }
        user = User.objects.create_user(**user_params)

        SecurityAnswer.objects.create(user=user,
                                      question=serializer.validated_data['question_one'],
                                      answer=serializer.validated_data['question_one_answer'])

        SecurityAnswer.objects.create(user=user,
                                      question=serializer.validated_data['question_two'],
                                      answer=serializer.validated_data['question_two_answer'])

        invite.status = EmailInvite.STATUS_ACCEPTED
        invite.user = user

        invite.save()

        login_params = {
            'username': user.email,
            'password': serializer.validated_data['password']
        }

        user = authenticate(**login_params)

        # check if user is authenticated
        if not user or not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        # Log the user in with a session as well.
        auth_login(request, user)

        user_serializer = UserSerializer(instance=user)

        invite.advisor.user.email_user('Client has accepted your invitation',
            "Your client %s %s (%s) has accepted your invitation to BetaSmartz!"
                                %(user.first_name, user.last_name, user.email))

        return Response(user_serializer.data)


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
