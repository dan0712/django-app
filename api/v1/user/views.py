from django.db import transaction
from rest_framework import exceptions, parsers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from client.models import Client
from support.models import SupportRequest
from user.autologout import SessionExpire
from . import serializers
from .serializers import EmailNotificationsSerializer, \
    UserAdvisorSerializer, UserClientSerializer
from ..permissions import IsClient
from ..views import ApiViewMixin, BaseApiView


class MeView(BaseApiView):
    serializer_class = serializers.UserSerializer

    def get(self, request):
        """
        ---
        # Swagger

        response_serializer: serializers.UserSerializer
        """
        user = SupportRequest.target_user(request)
        if user.is_support_staff:
            sr = SupportRequest.get_current(self.request, as_obj=True)
            user = sr.user
        data = self.serializer_class(user).data
        if user.is_advisor:
            role = 'advisor'
            data.update(UserAdvisorSerializer(user.advisor).data)
        elif user.is_client:
            role = 'client'
            data.update(UserClientSerializer(user.client).data)
        else:
            raise PermissionDenied("User is not in the client or "
                                   "advisor groups.")
        data.update({'role': role})
        return Response(data)

    @transaction.atomic
    def post(self, request):
        """
        ---
        # Swagger

        request_serializer: serializers.UserUpdateSerializer
        response_serializer: serializers.UserSerializer
        """
        user = SupportRequest.target_user(request)
        serializer = serializers.UserUpdateSerializer(user, data=request.data,
                                                      partial=True,
                                                      context={
                                                          'request': request,
                                                      })

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class LoginView(BaseApiView):
    """
    Signin andvisors or any other type of users
    """
    authentication_classes = ()
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserSerializer
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,
    )

    def post(self, request):
        """
        ---
        # Swagger

        request_serializer: serializers.AuthSerializer
        response_serializer: serializers.UserSerializer

        responseMessages:
            - code: 400
              message: Unable to log in with provided credentials
        """
        auth_serializer = serializers.AuthSerializer(data=request.data)

        auth_serializer.is_valid(raise_exception=True)
        user = auth_serializer.validated_data['user']

        # check if user is authenticated
        if not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class RegisterView(BaseApiView):
    pass


class ResetView(BaseApiView):
    def post(self, request):
        serializer = serializers.ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # set password
        user.set_password(serializer.validated_data['password'])
        user.save()

        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetEmailView(BaseApiView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = serializers.ResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_active:
            # send password
            pass
            return Response(status=status.HTTP_200_OK)
        return Response('User is blocked', status=status.HTTP_403_FORBIDDEN)


class KeepAliveView(BaseApiView):
    def get(self, request):
        SessionExpire(request).keep_alive()
        return Response('ok', status=status.HTTP_200_OK)


class EmailNotificationsView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = EmailNotificationsSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user).notification_prefs
