from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, parsers, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from main.models import User
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *
from api.v1.utils.helpers import *

import api.v1.user.serializers as serializers


class MeView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get(self, request):
        """
        ---
        # Swagger

        response_serializer: serializers.UserSerializer
        """
        user = self.request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

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
        #        serializer_client = serializers.InvestorUpdateSerializer(
        #            data=data_client, context={'request': request})
        #        serializer_client.is_valid(raise_exception=True)
        #        serializer_client.save()

        user = serializer.save()
        #advisor = serializer_advisor.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class LoginView(views.APIView):
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


class RegisterView(views.APIView):
    pass


class ResetView(views.APIView):
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


class ResetEmailView(views.APIView):
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


# TODO: obsoleted?
class APIUser(views.APIView):
    def get(self, request, format=None):
        """
        ---
        response_serializer: UserSerializer

        """
        try:

            user = self.request.user

            user_data = UserSerializer(user).data

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['status'] = 'error'
                if hasattr(e, 'message'):
                    response['message'] = str(e.message)

            raise ExceptionDefault(detail=response)

        content = {
            'user': user_data,
        }

        return Response(content)


# TODO: obsoleted?
class APIUserLevel(views.APIView):
    def get(self, request, format=None):
        """
        ---
        type:
          advisor:
            type: boolean
          client:
            type: boolean
        """
        try:

            # by default lets just set both false.
            client = False
            advisor = False

            user = self.request.user

            # check if they have client node
            if hasattr(user, 'client'):
                # now check if client node is not NULL
                if user.client is not None:
                    client = True

            # check if they have advisor node
            if hasattr(user, 'advisor'):
                # now check if advisor node is not NULL
                if user.advisor is not None:
                    advisor = True

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'client': client,
            'advisor': advisor,
        }

        return Response(content)


# TODO: obsoleted
class APIAccessToken(views.APIView):
    permission_classes = ()

    def post(self, request, format=None):
        """
        ---
        type:
          username:
            type: string
            required: true
          password:
            type: string
            required: true
        """
        try:

            username = self.request.data.get('username', None)

            password = self.request.data.get('password', None)

            # check for any missing field.
            if username is None or username == '':
                raise ExceptionDefault(detail=response_missing_fields(field='username'))

            if validate_email(username) is False:
                raise ExceptionDefault(detail=response_invalid_email_address())

            if password is None or password == '':
                raise ExceptionDefault(detail=response_missing_fields(field='password'))

            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                raise ExceptionDefault(detail=response_account_not_found())

            # TODO: funny, yes? :(
            user = authenticate(username=user.email, password=password)

            token, created = Token.objects.get_or_create(user=user)

        except Exception as e:

            if hasattr(e, 'detail'):
                response = e.detail

            else:
                response = dict()
                response['status'] = 'error'
                if hasattr(e, 'message'):
                    response['message'] = str(e.message)

            raise ExceptionDefault(detail=response)

        content = {
            'token': token.key,
        }

        return Response(content)


