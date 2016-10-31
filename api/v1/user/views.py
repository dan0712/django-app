import logging

from django.conf import settings
from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_reset
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import exceptions, parsers, status, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.v1.advisor.serializers import AdvisorSerializer
from api.v1.client.serializers import ClientFieldSerializer
from client.models import EmailInvite

from support.models import SupportRequest
from user.autologout import SessionExpire
from user.models import SecurityAnswer, SecurityQuestion
from . import serializers
from ..user.serializers import ChangePasswordSerializer, \
    ResetPasswordSerializer, SecurityAnswerCheckSerializer, \
    SecurityQuestionSerializer, SecurityQuestionAnswerUpdateSerializer

from ..client.serializers import InvitationSerializer
from ..views import ApiViewMixin, BaseApiView

logger = logging.getLogger('api.v1.user.views')


class PhoneNumberValidationView(ApiViewMixin, views.APIView):
    serializer_class = serializers.PhoneNumberValidationSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (
        parsers.JSONParser,
    )

    def post(self, request):
        """
        ---
        # Swagger
        request_serializer: serializers.PhoneNumberValidationSerializer
        response_serializer: serializers.PhoneNumberValidationSerializer

        responseMessages:
            - code: 400
              message: Invalid phone number
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


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
            data['advisor'] = AdvisorSerializer(user.advisor).data
        elif user.is_client:
            role = 'client'
            data['client'] = ClientFieldSerializer(user.client).data
        elif user.invitation and user.invitation.status == EmailInvite.STATUS_ACCEPTED:
            role = 'client'
            data['invitation'] = InvitationSerializer(instance=user.invitation).data
        else:
            raise PermissionDenied("User is not in the client or advisor groups, or is not a new user accepting an invitation.")
        data.update({'role': role})
        return Response(data)

    @transaction.atomic
    def put(self, request):
        """
        ---
        # Swagger

        request_serializer: serializers.UserUpdateSerializer
        response_serializer: serializers.UserSerializer
        """
        user = SupportRequest.target_user(request)
        if user.is_support_staff:
            sr = SupportRequest.get_current(self.request, as_obj=True)
            user = sr.user
        serializer = serializers.UserUpdateSerializer(user,
                                                      data=request.data,
                                                      partial=True,
                                                      context={
                                                          'request': request,
                                                      })

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        data = self.serializer_class(user).data
        if user.is_advisor:
            role = 'advisor'
            data['advisor'] = AdvisorSerializer(user.advisor).data
        elif user.is_client:
            role = 'client'
            # If the user wants to update client details, they do it through the specific client endpoint.
            data['client'] = ClientFieldSerializer(user.client).data
        else:
            raise PermissionDenied("User is not in the client or "
                                   "advisor groups.")
        data.update({'role': role})
        return Response(data)


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

        # Log the user in with a session as well.
        auth_login(request, user)

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


class PasswordResetView(ApiViewMixin, views.APIView):
    """
    accepts post with email field
    resets password and then
    sends reset password email to matching user account
    """
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer
    post_reset_redirect = '/password/reset/done/'

    # eventually just remove this
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
        return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class ChangePasswordView(ApiViewMixin, views.APIView):
    """
    allows logged in users to change their password
    receives old password, new password, and security question answer
    """
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

        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            logger.info('Changing password for user %s' % request.user.email)
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            # Django invalidates session on password change, so update session hash
            update_session_auth_hash(request, request.user)
            return Response('ok', status=status.HTTP_200_OK)
        logger.error('Unauthorized change password attempt from user %s' % request.user.email)
        return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class SecurityQuestionListView(ApiViewMixin, ListAPIView):
    """
    A read only list view.  Receives get request, returns
    a list of canned security questions set by admin usable
    by any authenticated user.
    """
    queryset = SecurityQuestion.objects.all()
    permission_classes = ()
    serializer_class = SecurityQuestionSerializer

    def get(self, request):
        # return set of canned security questions
        queryset = self.get_queryset()
        serializer = serializers.SecurityQuestionSerializer(queryset, many=True)
        return Response(serializer.data)


class SecurityQuestionAnswerView(ApiViewMixin, views.APIView):
    """
    allows a logged in user to POST a new security question and answer combinations
    and allows a logged user to GET a list of their security questions
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.SecurityUserQuestionSerializer

    def get(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = SecurityAnswer.objects.filter(user=request.user)
        serializer = serializers.SecurityUserQuestionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        # add new security question and answer combination
        user = request.user

        # check if question already exists for user
        if SecurityAnswer.objects.filter(user=user, question=request.data.get('question')).exists():
            return Response({'error': 'question already exists'}, status=status.HTTP_409_CONFLICT)

        serializer = serializers.SecurityAnswerSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            logger.info('Valid request to set new security question and answer for user %s' % request.user.email)
            serializer.save()
            return Response('ok', status=status.HTTP_200_OK)
        logger.error('Unauthorized attempt to set new security question and answer for user %s' % request.user.email)
        return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class SecurityQuestionAnswerUpdateView(ApiViewMixin, views.APIView):
    """
    allows an authenticated user to modify one of their security
    question answer combinations
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SecurityQuestionAnswerUpdateSerializer

    def post(self, request, pk):
        try:
            sa = SecurityAnswer.objects.get(pk=pk)
        except:
            logger.error('Request to update security answer with pk %s not found' % pk)
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.pk != sa.user.pk:
            logger.error('Unauthorized attempt by user %s to update security answer for user %s' % (request.user, sa.user))
            return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.SecurityQuestionAnswerUpdateSerializer(data=request.data, context={'pk': pk})
        if serializer.is_valid():
            logger.info('Valid request to update security answer for user %s and pk %s' % (request.user.email, pk))
            sa.question = serializer.validated_data['question']
            sa.set_answer(serializer.validated_data['answer'])
            sa.save()
            return Response('ok', status=status.HTTP_200_OK)
        logger.error('Unauthorized attempt to update security answer for user %s and pk %s' % (request.user.email, pk))
        return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class SecurityAnswerCheckView(ApiViewMixin, views.APIView):
    """
    allows authenticated request to check an answer is correct
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SecurityAnswerCheckSerializer

    def post(self, request, pk):
        try:
            sa = SecurityAnswer.objects.get(pk=pk)
        except:
            logger.error('Request to check security answer with pk %s not found' % pk)
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.pk != sa.user.pk:
            if not request.user.is_staff:
                # superusers are ok to update other user's security question answers
                logger.error('Unauthorized attempt by user %s to check security answer for user %s' % (request.user, sa.user))
                return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.SecurityAnswerCheckSerializer(data=request.data, context={'user': request.user, 'pk': pk})
        if serializer.is_valid():
            logger.info('Valid request to set check security answer for user %s and question %s' % (request.user.email, request.data.get('question')))
            return Response('ok', status=status.HTTP_200_OK)
        logger.error('Unauthorized attempt to check answer for user %s and question %s' % (request.user.email, request.data.get('question')))
        return Response({'error': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


