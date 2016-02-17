from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from main.models import User

from rest_framework import exceptions, serializers

#from ..models import Advisor, Client


__all__ = (
    #'FieldUserSerializer',
    'AuthTokenSerializer', 'UserSerializer',
    'SignupSerializer', 'ResetSerializer', 'ResetEmailSerializer',
)


class FieldUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            'is_staff', 'is_superuser',
            'password', 'last_login',
            'user_permissions', 'groups',
            #'is_active'
        )


# based on rest_framework.authtoken.serializers.AuthTokenSerializer
class AuthTokenSerializer(serializers.Serializer):
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


class UserSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    """
    token = serializers.SerializerMethodField(read_only=True)
    #advisor = serializers.SerializerMethodField()
    #client = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = (
            'is_staff', 'is_active', 'is_superuser',
            'password',
        )

    def get_token(self, obj):
        user = obj
        token = user.get_token()
        return token.key

    # RESERVED
    #def get_advisor(self, obj):
    #    user = obj
    #    if user.is_advisor:
    #        return UserAdvisorSerializer(user.advisor).data

    # RESERVED
    #def get_client(self, obj):
    #    user = obj
    #    if user.is_client:
    #        return UserClientSerializer(user.client).data


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

