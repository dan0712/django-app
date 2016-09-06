import logging

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import User
from user.models import SecurityAnswer, SecurityQuestion

logger = logging.getLogger('api.v1.user.serializers')


class UserFieldSerializer(ReadOnlyModelSerializer):
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


class UserSerializer(ReadOnlyModelSerializer):
    """
    For Read (GET) requests only
    """
    class Meta:
        model = User
        exclude = (
            'prepopulated',
            'is_staff', 'is_active', 'is_superuser',
            'password',
            'user_permissions',
            'groups', 'username'
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
    checks that question and answer matches one of the current user's
    security question/answer combos
    """
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    question = serializers.CharField()
    answer = serializers.CharField()

    def validate(self, data):
        # check security answer matches security question
        user = self.context.get('user')
        # validate old_password first
        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError('Wrong password')

        # validate security question and answer combo
        try:
            sa = SecurityAnswer.objects.get(user=user, question=data.get('question'))
        except:
            raise serializers.ValidationError('SecurityAnswer not found for user %s and question %s' % (user.email, data.get('question')))
        if not sa.check_answer(data.get('answer')):
            raise serializers.ValidationError('Wrong answer')
        return data


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    Returns list of canned security questions.
    """
    class Meta:
        model = SecurityQuestion
        fields = ('question', )


class SecurityUserQuestionSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    Returns a list of a given user's security answer objects,
    questions, id and user only no answer.
    """
    class Meta:
        model = SecurityAnswer
        fields = ('id', 'question', 'user')


class SecurityAnswerSerializer(serializers.Serializer):
    """
    For POST requests only
    Validates password for the user and sets a new question/answer
    """
    password = serializers.CharField()
    question = serializers.CharField()
    answer = serializers.CharField()

    def validate(self, data):
        user = self.context.get('user')
        if not user.check_password(data.get('password')):
            raise serializers.ValidationError('Wrong password')

        # check if question already exists for user
        if SecurityAnswer.objects.filter(user=user, question=data.get('question')).exists():
            raise serializers.ValidationError('SecurityAnswer already exists')
        return data

    def create(self, validated_data):
        user = self.context.get('user')
        sa = SecurityAnswer.objects.create(user=user, question=validated_data.get('question'))
        sa.set_answer(validated_data.get('answer'))
        sa.save()
        return sa


class SecurityQuestionAnswerUpdateSerializer(serializers.Serializer):
    """
    For POST requests only
    Validates the given question's old answer, and updates the question/answer
    """
    old_answer = serializers.CharField()
    question = serializers.CharField(required=False)
    answer = serializers.CharField(required=False)

    def validate_old_answer(self, value):
        pk = self.context.get('pk')
        try:
            sa = SecurityAnswer.objects.get(pk=pk)
        except:
            raise serializers.ValidationError('SecurityAnswer not found with pk %s' % pk)
        if sa.has_usable_answer():
            if not sa.check_answer(value):
                raise serializers.ValidationError('Wrong answer')
        else:
            raise serializers.ValidationError('No usable answer')
        return value


class SecurityAnswerCheckSerializer(serializers.Serializer):
    """
    For POST requests only
    Validates a security answer is correct for the current user
    """
    answer = serializers.CharField()

    def validate(self, data):
        user = self.context.get('user')
        try:
            sa = SecurityAnswer.objects.get(user=user, pk=self.context.get('pk'))
        except:
            raise serializers.ValidationError('SecurityAnswer not found for user %s and question %s' % (user.email, data.get('question')))
        if sa.has_usable_answer():
            if not sa.check_answer(data.get('answer')):
                raise serializers.ValidationError('Wrong answer')
        else:
            raise serializers.ValidationError('No usable answer')
        return data
