import logging

from django.db import transaction
from rest_framework import serializers

from main.models import (
    ClientAccount,
    Goal, GoalSetting, GoalMetric, GoalTypes,
    Position, Portfolio, PortfolioItem, 
    RecurringTransaction, AssetFeatureValue,
    StandardAssetFeatureValues
)
from portfolios.management.commands.portfolio_calculation import (
    get_instruments, calculate_portfolio, Unsatisfiable
)
from portfolios.management.commands.risk_profiler import recommend_risk


__all__ = (
    'GoalSerializer',
    'GoalListSerializer',
    'GoalUpdateSerializer',
    'GoalTypeListSerializer',
)


logger = logging.getLogger('goal_serializer')


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = (
            'asset',
            'weight',
            'volatility',
        )


class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(many=True)

    class Meta:
        model = Portfolio
        fields = (
            'variance',
            'er',
            'items',
        )


class RecurringTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringTransaction
        fields = (
            'recurrence',
            'enabled',
            'amount',
        )


class GoalMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalMetric
        exclude = (
            'id',
            'setting',
        )


class GoalMetricCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalMetric


class GoalSettingSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer()
    metrics = GoalMetricSerializer(many=True)
    recurring_transactions = RecurringTransactionSerializer(many=True)

    class Meta:
        model = GoalSetting
        exclude = (
            'id',
        )


class GoalSettingCreateSerializer(serializers.ModelSerializer):
    metrics = GoalMetricSerializer(many=True)
    recurring_transactions = RecurringTransactionSerializer(many=True)
    portfolio = PortfolioSerializer()

    class Meta:
        model = GoalSetting
        fields = (
            'target',
            'completion',
            'hedge_fx',
            'metrics',
            'recurring_transactions',
            'portfolio'
        )

    def create(self, validated_data):
        goal = validated_data.pop('goal')
        metrics_data = validated_data.pop('metrics')
        tx_data = validated_data.pop('recurring_transactions')
        port_data = validated_data.pop('portfolio')
        port_items_data = port_data.pop('items')
        with transaction.atomic():
            port = Portfolio.objects.create(**port_data)
            PortfolioItem.objects.bulk_create([PortfolioItem(portfolio=port, **i_data) for i_data in port_items_data])
            setting = GoalSetting.objects.create(portfolio=port, **validated_data)
            RecurringTransaction.objects.bulk_create([RecurringTransaction(setting=setting, **i_data) for i_data in tx_data])
            GoalMetric.objects.bulk_create([GoalMetric(setting=setting, **i_data) for i_data in metrics_data])
            old_setting = goal.selected_settings
            goal.selected_settings = setting
            goal.save()
            old_setting.delete()

        return setting


class GoalSerializer(serializers.ModelSerializer):
    # TODO: Make created read only.
    class Meta:
        model = Goal
        exclude = (
            'active_settings',
        )


class GoalListSerializer(serializers.ModelSerializer):
    """
    Light version of GoalSerializer
    """
    class Meta:
        model = Goal
        fields = (
            'id',
            'name',
        )


class GoalCreateSerializer(serializers.ModelSerializer):
    target = serializers.IntegerField()
    completion = serializers.DateField()
    initial_deposit = serializers.IntegerField(required=False)
    ethical = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Goal
        fields = (
            'account',
            'portfolio_set',
            'name',
            'type',
            'target',
            'completion',
            'initial_deposit',
            'ethical',
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
        Override the default create because we need to generate a portfolio.
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

            # Based on the risk profile, and whether an ethical profile was specified on creation, set up Metrics.
            recommended_risk = recommend_risk(settings)
            GoalMetric.objects.create(setting=settings,
                                      type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                      comparison=GoalMetric.METRIC_COMPARISON_EXACTLY,
                                      rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                      rebalance_thr=0.05,
                                      configured_val=recommended_risk)
            if validated_data['ethical']:
                GoalMetric.objects.create(
                    setting=settings,
                    type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                    feature=StandardAssetFeatureValues.SRI_OTHER.get_object(),
                    comparison=GoalMetric.METRIC_COMPARISON_EXACTLY,
                    rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                    rebalance_thr=0.05,
                    configured_val=1  # Start with 100% ethical.
                )

            # TODO: Add the initial deposit logic.

            # Calculate the optimised portfolio
            try:
                weights, er, variance = calculate_portfolio(settings, idata)
                items = [PortfolioItem(portfolio=portfolio,
                                       asset=idata[2].loc[sym, 'id'],
                                       weight=weight,
                                       volatility=idata[0].loc[sym, sym]) for sym, weight in weights.items()]
                PortfolioItem.objects.bulk_create(items)
                portfolio.variance = variance
                portfolio.er = er
                portfolio.save()
            except Unsatisfiable:
                # TODO: Return a message to the user that because they didn't make an initial deposit, we couldn't
                # come up with an appropriate portfolio, and they need to make a deposit to get started.
                logger.exception("No suitable portfolio could be found. Leaving empty.")

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
