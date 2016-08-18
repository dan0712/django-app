import logging

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from api.v1.serializers import ReadOnlyModelSerializer
from client.models import Client, EmailNotificationPrefs
from main.models import Advisor, User
from support.models import SupportRequest
from user.models import SecurityAnswer, SecurityQuestion

logger = logging.getLogger('api.v1.user.serializers')


class FieldUserSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = User
        exclude = (
            'is_staff', 'is_superuser',
            'password', 'last_login',
            'user_permissions', 'groups',
            'prepopulated', 'is_active'
        )


class AuthSerializer(serializers.Serializer):
    """
    based on rest_framework.authtoken.serializers.AuthTokenSerializer
    """
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        identification = 'email' if attrs.get('email') else 'username'

        credentials = {
            'password': attrs.get('password'),
            identification: attrs.get(identification),
        }

        if credentials[identification] and credentials['password']:
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" or "username" and "password".')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class UserAdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor
        exclude = (
            'user',
            'confirmation_key',
            'letter_of_authority', 'betasmartz_agreement',
        )


class UserClientSerializer(serializers.ModelSerializer):
    advisor = serializers.SerializerMethodField()

    class Meta:
        model = Client
        exclude = (
            'user',
            'client_agreement',
            'confirmation_key',
            # filter out more fields if needed
            'create_date',
        )

    def get_advisor(self, obj):
        client = obj
        if client.advisor:
            return UserClientAdvisorSerializer(client.advisor).data


class UserClientAdvisorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'prepopulated',
            'is_staff', 'is_superuser',
            'password', 'last_login',
            'user_permissions', 'groups',
            'username', 'email',
            'date_joined',
            'is_active',
        )


class UserClientAdvisorSerializer(serializers.ModelSerializer):
    user = UserClientAdvisorUserSerializer()

    class Meta:
        model = Advisor
        fields = (
            'id',
            'gender',
            'work_phone_num',
            'user',
            'firm',
            'email'
        )


class UserSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    """
    class Meta:
        model = User
        exclude = (
            'prepopulated',
            'is_staff', 'is_active', 'is_superuser',
            'password',
            'user_permissions',
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    For write (POST/PUT/...) requests only
    """
    oldpassword = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    password2 = serializers.CharField(required=False)
    # TODO: add fields to update advisor and client profiles

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'password', 'password2', 'oldpassword',
        )

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if data.get('password'):
            if data.get('password') != data.get('password2'):
                raise serializers.ValidationError('Passwords are not equal')

            if not user.check_password(data.get('oldpassword')):
                raise serializers.ValidationError('Invalid current password')

        return data


class AdvisorUpdateSerializer(serializers.ModelSerializer):
    """
    For write (POST/PUT/...) requests only
    """
    class Meta:
        model = Advisor
        fields = (
        #'firm',
        )


class ClientUpdateSerializer(serializers.ModelSerializer):
    """
    For write (POST/PUT/...) requests only
    """
    class Meta:
        model = Client
        fields = (
        'advisor',
        )

    def __init__(self, *args, **kwargs):
        super(ClientUpdateSerializer, self).__init__(*args, **kwargs)

        # request based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

        user = SupportRequest.target_user(request)

        # experimental / for advisors only
        if user.is_advisor:
            advisor = user.advisor

            self.fields['advisor'].queryset = \
                self.fields['advisor'].queryset.filter(pk=advisor.pk)


class ResetSerializer(serializers.Serializer):
    """
    For write (POST...) requests only
    """
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, value):
        if value.get('password'):
            if value.get('password') != value.get('password2'):
                raise serializers.ValidationError('Passwords are not equal')

        return value


class ResetEmailSerializer(serializers.Serializer):
    """
    For write (POST...) requests only
    """
    email = serializers.EmailField()
    domain = serializers.CharField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email address not found')

        return value


class EmailNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotificationPrefs
        exclude = 'id', 'client',


class ResetPasswordSerializer(serializers.Serializer):
    """
    receives email address, checks if user exists, send password reset email
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            emsg = 'User not found matching email address %s' % value
            logging.error(emsg)
            raise serializers.ValidationError(emsg)
        return value

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class ChangePasswordSerializer(serializers.Serializer):
    """
    checks old password matches current user password,
    checks that answer matches current user security answer
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    answer = serializers.CharField()

    def validate_answer(self, value):
        # check security answer matches security question
        try:
            sa = SecurityAnswer.objects.get(user=self.context.get('request').user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('User does not exist')
        if sa.check_answer(value):
            raise serializers.ValidationError('Wrong answer')
        return value

    def validate_old_password(self, value):
        # check old password matches
        if not self.context.get('request').user.check_password(value):
            raise serializers.ValidationError('Wrong password')
        return value


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    Returns list of canned security questions.
    """
    class Meta:
        model = SecurityQuestion
        fields = ['question', ]


class SecurityUserQuestionSerializer(serializers.Serializer):
    """

    """
    question = serializers.CharField()

    def validate(self, data):
        # validation handled in view for this mostly
        # returns 404 if not found, otherwise the user's question
        return data


class SecurityAnswerSerializer(serializers.Serializer):
    """
    For POST requests only
    Validates an old answer and sets a new question/answer
    """
    old_answer = serializers.CharField(required=False)
    question = serializers.CharField()
    answer = serializers.CharField()

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        try:
            sa = SecurityAnswer.objects.get(user=user)
        except:
            # if the security answer doesn't exist for the current user
            # that's ok, we're setting their security question/answer combo
            # for the first time now
            return data
        if sa.has_usable_answer():  # check an answer was set
            if not sa.check_answer(data.get('old_answer')):
                raise serializers.ValidationError('Wrong answer')
        return data


class SecurityAnswerCheckSerializer(serializers.Serializer):
    """
    For POST requests only
    Validates a security answer is correct for the current user
    """

    answer = serializers.CharField()

    def validate_answer(self, value):
        user = self.context.get('request').user
        try:
            sa = SecurityAnswer.objects.get(user=user)
        except:
            raise serializers.ValidationError('SecurityAnswer not found for user %s' % user.email)
        if not sa.check_answer(value):
            raise serializers.ValidationError('Wrong answer')
        return value
