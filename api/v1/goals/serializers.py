from rest_framework import serializers

from main.models import (
    Goal, GoalSetting, GoalTypes,
    ClientAccount, Position,
)

__all__ = (
    'GoalSerializer',
    'GoalListSerializer',
    'GoalUpdateSerializer',
    'GoalTypeListSerializer',
)


class GoalClientAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAccount
        #exclude = (
        #    'id',
        #)


class GoalGoalSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalSetting
        exclude = (
            #'created_at',
        )


class GoalSerializer(serializers.ModelSerializer):
    account = GoalClientAccountSerializer()
    settings = GoalGoalSettingSerializer(source='active_settings')
    #approved_settings = GoalGoalSettingSerializer()
    #selected_settings = GoalGoalSettingSerializer()

    class Meta:
        model = Goal
        exclude = (
            'created',
            'active_settings',
            'approved_settings', 'selected_settings',
        )


class GoalListSerializer(serializers.ModelSerializer):
    settings = GoalGoalSettingSerializer(source='active_settings')

    """
    Light version of GoalSerializer
    """
    class Meta:
        model = Goal
        exclude = (
            'created',
            'active_settings',
            'approved_settings', 'selected_settings',
        )


class GoalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = (
            'account',
            'name',
            'type',
        ) # list fields explicitly

    def __init__(self, *args, **kwargs):
        super(GoalCreateSerializer, self).__init__(*args, **kwargs)

        # request-based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

        user = request.user

        # experimental / for advisors
        if user.is_advisor:
            self.fields['account'].queryset = \
                self.fields['account'].queryset.filter_by_advisor(user.advisor)

        # experimental / for clients
        # TEMP set default account
        if user.is_client:
            self.fields['account'].required = False
            self.fields['account'].default = user.client.accounts.all().first()
            self.fields['account'].queryset = \
                self.fields['account'].queryset.filter_by_client(user.client)


class GoalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = (
            'name',
        ) # list fields explicitly

    def __init__(self, *args, **kwargs):
        super(GoalUpdateSerializer, self).__init__(*args, **kwargs)

        # request based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

        #user = request.user

        # experimental / for advisors only
        #if user.is_advisor:
        #    self.fields['account'].queryset = \
        #        self.fields['account'].queryset.filter_by_advisor(user.advisor)


class GoalGoalTypeListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = GoalTypes


class GoalPositionListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = Position
