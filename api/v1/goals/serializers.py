from rest_framework import serializers

from main.models import (
    Goal, GoalTypes, ClientAccount,
    Position,
)

__all__ = (
    'GoalSerializer', 'GoalListSerializer',
    'GoalUpdateSerializer',
    'GoalTypeListSerializer',
)


class GoalClientAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAccount
        #exclude = (
        #    'id',
        #)


class GoalSerializer(serializers.ModelSerializer):
    account = GoalClientAccountSerializer()

    class Meta:
        model = Goal


class GoalListSerializer(serializers.ModelSerializer):
    """
    Light version of GoalSerializer
    """
    class Meta:
        model = Goal
        exclude = (
            'portfolios',
            'created_date', 'completion_date',
        )


class GoalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = (
            'account',
            'name',
            'target', 'income',
            'completion_date', 'allocation',
            'drift', 'duration', 'initialDeposit', 'amount',
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
            'name', 'target',
            'duration', 'initialDeposit',
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
