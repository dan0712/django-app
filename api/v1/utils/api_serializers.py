from django.core.cache import *
from django.db.models import Count
from main.models import *
from django.db.models import Count, Min, Sum, Avg
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ('password',)

    def get_level(self, obj):
        # by default lets just set both false.
        client = False
        advisor = False

        # check if they have client node
        if hasattr(obj, 'client'):
            # now check if client node is not NULL
            if obj.client is not None:
                client = True

        # check if they have advisor node
        if hasattr(obj, 'advisor'):
            # now check if advisor node is not NULL
            if obj.advisor is not None:
                advisor = True

        return {'client': client, 'advisor': advisor}


class GoalTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTypes


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal


class AdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor


class AccountGroupSerializer(serializers.ModelSerializer):
    advisor = AdvisorSerializer()
    secondary_advisors = AdvisorSerializer(many=True)

    class Meta:
        model = AccountGroup


class ClientSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()

    last_name = serializers.SerializerMethodField()

    email = serializers.SerializerMethodField()

    class Meta:
        model = Client

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email


class ClientAccountSerializer(serializers.ModelSerializer):
    account_group = AccountGroupSerializer()

    goals = serializers.SerializerMethodField()

    class Meta:
        model = ClientAccount

    def get_goals(self, obj):
        return GoalSerializer(obj.goals, many=True).data
