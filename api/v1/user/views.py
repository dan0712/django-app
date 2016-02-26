from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# TODO: drop unused imports after removing obsoleted endpoints
from api.v1.user.serializers import UserAdvisorSerializer, UserClientSerializer
from main.models import User, ClientAccount, Goal

from ..clients import serializers as clients_serializers
from ..goals import serializers as goals_serializers
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisor,
    IsClient,
    IsMyAdvisorCompany,
    IsAdvisorOrClient,
)
from . import serializers


class MeView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get(self, request):
        """
        ---
        # Swagger

        response_serializer: serializers.UserSerializer
        """
        user = self.request.user
        data = self.serializer_class(user).data
        if user.is_advisor:
            role = 'advisor'
            data.update(UserAdvisorSerializer(user.advisor).data)
        elif user.is_client:
            role = 'client'
            data.update(UserClientSerializer(user.client).data)
        data.update({ 'role': role })
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
        serializer = serializers.UserUpdateSerializer(user,
            data=request.data, partial=True, context={'request': request})

        serializer.is_valid(raise_exception=True)

        # reserved
        #if user.is_advisor:
        #    data_advisor = self.get_nested_data('advisor__')
        #
        #    if data_advisor:
        #        serializer_advisor = serializers.AdvisorUpdateSerializer(
        #            user.advisor, data=data_advisor, partial=True)
        #
        #        serializer_advisor.is_valid(raise_exception=True)
        #        serializer_advisor.save()
        #
        #    data_advisor_address = self.get_nested_data('advisor__address__')
        #    if data_advisor_address:
        #        serializer_advisor_address = serializers.AdvisorUpdateSerializer(
        #            user.advisor.address, data=data_advisor_address, partial=True)
        #        serializer_advisor_address.is_valid(raise_exception=True)
        #        serializer_advisor_address.save()
        #
        #if user.is_client:
        #    data_client = self.get_nested_data('client__')
        #    if data_client:
        #        serializer_client = serializers.ClientUpdateSerializer(
        #            data=data_client, context={'request': request})
        #        serializer_client.is_valid(raise_exception=True)
        #        serializer_client.save()

        user = serializer.save()
        #advisor = serializer_advisor.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class MeAccountsView(ApiViewMixin, views.APIView):
    serializer_class = clients_serializers.ClientAccountListSerializer
    permission_classes = (IsClient,)

    def get(self, request):
        user = self.request.user
        client = user.client
        accounts = client.accounts_all.all()

        serializer = self.serializer_class(accounts, many=True)
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

    #def get_serializer_class(self):
    #    return self.serializer_class

    def post(self, request):
        """
        ---
        # Swagger

        request_serializer: serializers.AuthTokenSerializer
        response_serializer: serializers.UserSerializer

        responseMessages:
            - code: 400
              message: Unable to log in with provided credentials
        """
        token_serializer = serializers.AuthTokenSerializer(data=request.data)

        token_serializer.is_valid(raise_exception=True)
        user = token_serializer.validated_data['user']

        # check if user is authenticated
        if not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        # check if user is allowed to enter
        #if not user.is_advisor:
        #    raise exceptions.PermissionDenied()

        # let's (re)create token
        token = Token.objects.get_or_create(user=user)

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

        # reset token
        # no need to
        #token = Token.objects.get(user=user)
        #token.key = token.generate_key()
        #token.save()

        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetEmailView(ApiViewMixin, views.APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = serializers.ResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.is_active:
            # send password
            pass
            return Response(status=status.HTTP_200_OK)

        else:
            return Response('User is blocked', status=status.HTTP_403_FORBIDDEN)
