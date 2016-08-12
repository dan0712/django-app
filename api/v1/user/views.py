from django.db import transaction
from rest_framework import exceptions, parsers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from client.models import Client
from user.autologout import SessionExpire
from . import serializers
from ..permissions import IsClient
from ..user.serializers import EmailNotificationsSerializer, \
    UserAdvisorSerializer, UserClientSerializer, ResetPasswordSerializer, \
    ChangePasswordSerializer
from ..views import ApiViewMixin
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.views import password_reset
import logging


logger = logging.getLogger('api.v1.user.views')


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
        SessionExpire(request).keep_alive()
        return Response('ok', status=status.HTTP_200_OK)


class EmailNotificationsView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = EmailNotificationsSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user).notification_prefs


class PasswordResetView(ApiViewMixin, views.APIView):
    # accepts post with email field
    # resets password and then
    # sends reset password email to matching user account
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer
    post_reset_redirect = '/password/reset/done/'

    def get(self, request):
        return password_reset(request,
                              self.post_reset_redirect,
                              template_name='registration/password_reset.html')

    def post(self, request):
        serializer = serializers.ResetPasswordSerializer(data=request.data)
        protocol = 'https' if request.is_secure else 'http'

        if serializer.is_valid():
            logger.info('Resetting password for user %s' % serializer.validated_data['email'])
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            for user in serializer.get_users(serializer.validated_data['email']):
                ctx = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': protocol,
                }
                serializer.send_mail(
                    subject_template_name='registration/password_reset_subject.txt',
                    email_template_name='registration/password_reset_email.html',
                    from_email=settings.SUPPORT_EMAIL,
                    to_email=user.email,
                    context=ctx,
                )
            return Response('ok', status=status.HTTP_200_OK)

        logger.error('Unauthorized login attempt using email %s' % serializer.data['email'])
        return Response('unauthorized', status=status.HTTP_401_UNAUTHORIZED)


class ChangePasswordView(ApiViewMixin, views.APIView):
    # allows logged in users to change their password
    # receives old password, new password, and security question answer
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        # camelCase to snake_case
        if 'oldPassword' in request.data:
            request.data['old_password'] = request.data['oldPassword']
            request.data.pop('oldPassword', None)
        if 'newPassword' in request.data:
            request.data['new_password'] = request.data['newPassword']
            request.data.pop('newPassword', None)

        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            logger.info('Changing password for user %s' % request.user.email)
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response('ok', status=status.HTTP_200_OK)
        logger.error('Unauthorized change password attempt from user %s' % request.user.email)
        return Response('unauthorized', status=status.HTTP_401_UNAUTHORIZED)
