from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *
from api.v1.utils.helpers import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout


class APIUser(APIView):
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


class APIUserLevel(APIView):
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


class APIAccessToken(APIView):
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
