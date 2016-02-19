from django.db import transaction
from rest_framework import serializers

from main.models import (
    Goal, GoalTypes, ClientAccount,
    Position,
    GoalSetting, Portfolio, PortfolioItem, RecurringTransaction)
from portfolios.management.commands.portfolio_calculation import get_instruments, calculate_portfolio

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


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = (
            'asset',
            'weight',
        )


class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(many=True)
    class Meta:
        model = Portfolio
        fields = (
            'variance',
            'er',
            'items'
        )


class RecurringTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringTransaction
        fields = (
            'recurrence',
            'enabled',
            'amount',
        )

class GoalSettingSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer()
    recurring_transactions = RecurringTransactionSerializer()

    class Meta:
        model = GoalSetting
        exclude = (
            'goal'
        )

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
            'created',
        )


class GoalCreateSerializer(serializers.ModelSerializer):
    target = serializers.IntegerField()
    completion = serializers.DateField()
    initial_deposit = serializers.IntegerField(required=False)

    class Meta:
        model = Goal
        fields = (
            'account',
            'name',
            'type',
            'target',
            'completion',
            'initial_deposit',
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

    def create(self, validated_data):
        """
        Override the default create because we need to generate a portfolio etc.
        :param validated_data:
        :return: The created Goal
        """
        account = validated_data['account']

        idata = get_instruments()

        with transaction.atomic():
            portfolio = Portfolio.objects.create(
                variance=0,
                er=0,
            )
            settings = GoalSetting.objects.create(
                target=validated_data['target'],
                completion=validated_data['completion'],
                hedge_fx=False,
                portfolio=portfolio,
            )
            goal = Goal.objects.create(
                account=account,
                name=validated_data['name'],
                type=validated_data['type'],
                portfolio_set=account.default_portfolio_set,
                selected_settings=settings,
            )

            # TODO: Based on the risk profile, and whether an ethical profile was specified on creation, set up Metrics.
            
            weights, er, variance = calculate_portfolio(goal, idata)
            items = [PortfolioItem(portfolio=portfolio,
                                   asset=k,
                                   weight=v,
                                   volatility=idata[0].loc[k, k]) for k, v in weights.items()]
            PortfolioItem.objects.bulk_create(items)
            portfolio.variance = variance
            portfolio.er = er
            portfolio.save()

        return goal


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
