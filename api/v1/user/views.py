from django.db import transaction
from rest_framework import exceptions, parsers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.v1.permissions import IsClient
from client.models import Client
from user.autologout import keep_alive
from . import serializers
from ..user.serializers import UserAdvisorSerializer, UserClientSerializer
from api.v1.client.serializers import EmailNotificationsSerializer
from ..views import ApiViewMixin


class MeView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get(self, request):
        """
        ---
        # Swagger

        response_serializer: serializers.UserSerializer
        """
        user = request.user
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
        user = self.request.user
        serializer = serializers.UserUpdateSerializer(user, data=request.data,
                                                      partial=True,
                                                      context={
                                                          'request': request,
                                                      })

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class LoginView(ApiViewMixin, views.APIView):
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


class RegisterView(ApiViewMixin, views.APIView):
    pass


class ResetView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = serializers.ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # set password
        user.set_password(serializer.validated_data['password'])
        user.save()

        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetEmailView(ApiViewMixin, views.APIView):
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


class KeepAliveView(ApiViewMixin, views.APIView):
    permission_classes = IsAuthenticated,

    def get(self, request):
        keep_alive(request)
        return Response('ok', status=status.HTTP_200_OK)
