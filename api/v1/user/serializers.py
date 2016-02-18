from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, serializers

from main.models import User, Advisor, Client


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


class UserAdvisorSerializer(serializers.ModelSerializer):
    #firm = UserFirmSerializer()

    class Meta:
        model = Advisor
        exclude = (
            'user',
            'confirmation_key',
            'security_question_1', 'security_question_2',
            'security_answer_1', 'security_answer_2',
            #'token', # what's the token?
            'letter_of_authority', 'betasmartz_agreement',
        )


class UserClientSerializer(serializers.ModelSerializer):
    advisor = serializers.SerializerMethodField()

    class Meta:
        model = Client
        exclude = (
            'user',
            'security_question_1', 'security_question_2',
            'security_answer_1', 'security_answer_2',
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
            'phone_number', 'work_phone',
            'user', 'firm',
        )


class UserSerializer(serializers.ModelSerializer):
    """
    For read (GET) requests only
    """
    token = serializers.SerializerMethodField(read_only=True)
    advisor = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = (
            'prepopulated',
            'is_staff', 'is_active', 'is_superuser',
            'password',
            'user_permissions',
        )

    def get_token(self, obj):
        user = obj
        token = user.get_token()
        return token.key

    def get_advisor(self, obj):
        user = obj
        if user.is_advisor:
            return UserAdvisorSerializer(user.advisor).data

    def get_client(self, obj):
        user = obj
        if user.is_client:
            return UserClientSerializer(user.client).data


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

        user = request.user

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

