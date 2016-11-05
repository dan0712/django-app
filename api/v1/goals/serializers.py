import logging

import copy

from django.db import transaction
from django.core.exceptions import ValidationError as CVE
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.fields import FloatField, IntegerField

from api.v1.serializers import EventMemoMixin, NoCreateModelSerializer, \
    NoUpdateModelSerializer, ReadOnlyModelSerializer
from main.event import Event
from main.models import AssetFeatureValue, Goal, GoalMetric, GoalMetricGroup, GoalSetting, GoalType, Portfolio, \
    PortfolioItem, RecurringTransaction, Ticker, Transaction
from main.risk_profiler import recommend_risk, validate_risk_score
from portfolios.calculation import Unsatisfiable, calculate_portfolio, current_stats_from_weights, get_instruments
from portfolios.providers.data.django import DataProviderDjango
from portfolios.providers.execution.django import ExecutionProviderDjango
from support.models import SupportRequest


logger = logging.getLogger('goal_serializer')


class PortfolioItemSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = PortfolioItem
        exclude = (
            'portfolio',
            'volatility',
        )


class PortfolioItemCreateSerializer(NoUpdateModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = (
            'asset',
            'weight',
        )


class PortfolioSerializer(ReadOnlyModelSerializer):
    """
    This is a read_only serializer.
    """
    items = PortfolioItemSerializer(many=True)

    class Meta:
        model = Portfolio
        exclude = (
            'setting',
        )


class PortfolioCreateSerializer(NoUpdateModelSerializer):
    """
    This is a read_only serializer.
    """
    items = PortfolioItemCreateSerializer(many=True)

    class Meta:
        model = Portfolio
        fields = (
            'items',
        )


class StatelessPortfolioItemSerializer(serializers.Serializer):
    asset = IntegerField()
    weight = FloatField()
    volatility = FloatField()


class PortfolioStatelessSerializer(serializers.Serializer):
    stdev = FloatField()
    er = FloatField()
    items = StatelessPortfolioItemSerializer(many=True)


class RecurringTransactionSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RecurringTransaction
        exclude = (
            'setting',
        )


class RecurringTransactionCreateSerializer(NoUpdateModelSerializer):
    class Meta:
        model = RecurringTransaction
        fields = (
            'schedule',
            'begin_date',
            'amount',
            'growth',
            'enabled',
        )


class TransactionCreateSerializer(NoUpdateModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'amount',
            'from_goal',
            'to_goal',
        )
        required_fields = (
            'amount'
        )


class GoalMetricSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = GoalMetric
        exclude = (
            'group',
        )


class GoalMetricCreateSerializer(NoUpdateModelSerializer):
    class Meta:
        model = GoalMetric
        fields = (
            'type',
            'feature',
            'comparison',
            'rebalance_type',
            'rebalance_thr',
            'configured_val'
        )


class GoalMetricGroupCreateSerializer(NoUpdateModelSerializer):
    metrics = GoalMetricCreateSerializer(many=True)

    class Meta:
        model = GoalMetricGroup
        fields = (
            'name',
            'metrics',
        )


class GoalMetricGroupSerializer(ReadOnlyModelSerializer):
    metrics = GoalMetricSerializer(many=True)

    class Meta:
        model = GoalMetricGroup
        fields = (
            'id',
            'name',
            'metrics',
        )

    def to_representation(self, instance):
        if instance.type == GoalMetricGroup.TYPE_CUSTOM:
            self.fields.pop("name", None)
        return super(GoalMetricGroupSerializer, self).to_representation(instance)


class GoalSettingSerializer(ReadOnlyModelSerializer):
    metric_group = GoalMetricGroupSerializer()
    recurring_transactions = RecurringTransactionSerializer(many=True)
    portfolio = PortfolioSerializer()

    class Meta:
        model = GoalSetting


class GoalSettingWritableSerializer(EventMemoMixin, serializers.ModelSerializer):
    metric_group = GoalMetricGroupCreateSerializer(required=True)
    recurring_transactions = RecurringTransactionCreateSerializer(many=True, required=False)
    portfolio = PortfolioCreateSerializer(required=False)

    class Meta:
        model = GoalSetting
        fields = (
            'target',
            'completion',
            'hedge_fx',
            'rebalance',
            'metric_group',
            'recurring_transactions',
            'portfolio',
            # These 2 are from the EventMemoMixin, and since we specify fields explicitly, we need to include them.
            'event_memo',
            'event_memo_staff',
        )

        required_fields = (
            # I don't know why, but these are not getting propagated from the model. Atually, they're even getting
            # ignored here.
            'hedge_fx',
            'completion',
        )

    def update(self, setting, validated_data):
        """
        Overwrite update to deal with nested writes.
        :param setting: The item we're updating
        :param validated_data:
        :return:
        """
        goal = validated_data.pop('goal')
        metrics_data = validated_data.pop('metric_group', None)
        tx_data = validated_data.pop('recurring_transactions', None)
        port_data = validated_data.pop('portfolio', None)

        with transaction.atomic():
            # Create a new setting.
            old_setting = setting
            setting = copy.copy(setting)
            setting.pk = None
            for attr, value in validated_data.items():
                if attr not in ['target', 'completion', 'hedge_fx', 'rebalance']:
                    raise ValidationError({"msg": "{} is not a valid field for updating a goal setting.".format(attr)})
                setattr(setting, attr, value)
            if metrics_data is not None:
                gid = metrics_data.get('id', None)
                if gid is None:
                    group = GoalMetricGroup.objects.create()
                    setting.metric_group = group
                    metrics = metrics_data.get('metrics')
                    mo = []
                    for i_data in metrics:
                        if 'measured_val' in i_data:
                            raise ValidationError({"msg": "measured_val is read-only"})
                        mo.append(
                            GoalMetric(
                                group=group,
                                type=i_data['type'],
                                feature=i_data.get('feature', None),
                                comparison=i_data['comparison'],
                                rebalance_type=i_data['rebalance_type'],
                                rebalance_thr=i_data['rebalance_thr'],
                                configured_val=i_data['configured_val'],
                            )
                        )
                    GoalMetric.objects.bulk_create(mo)
                else:
                    setting.metric_group = GoalMetricGroup.objects.get(gid)
            # Otherwise we just use the old settings object metric group that will be copied in the above copy()

            setting.save()

            # Do the portfolio.
            if port_data is None:
                # We can't just change the setting object the portfolio is pointing at as the old setting may still be
                # active as an approved setting. WE need to create a new portfolio by copying the old one.
                # We have to do it this way so the portfolio_id field on the setting is updated.
                if hasattr(old_setting, 'portfolio'):
                    new_port = copy.copy(old_setting.portfolio)
                    pxs = new_port.items.all()
                    new_port.id = None
                    new_port.setting = setting
                    new_port.save()
                    for item in pxs:
                        item.id = None
                        item.portfolio = new_port
                        item.save()
            else:
                port_items_data = port_data.pop('items')
                # Get the current portfolio statistics of the given weights.
                try:
                    er, stdev, idatas = current_stats_from_weights([(item['asset'].id,
                                                                             item['weight']) for item in port_items_data],
                                                                   DataProviderDjango()
                                                                   )
                except Unsatisfiable as e:
                    raise ValidationError(e.msg)
                port = Portfolio.objects.create(setting=setting, er=er, stdev=stdev)
                PortfolioItem.objects.bulk_create([PortfolioItem(portfolio=port,
                                                                 asset=i_data['asset'],
                                                                 weight=i_data['weight'],
                                                                 volatility=idatas[i_data['asset'].id]) for i_data in port_items_data])

            # Do the recurring transactions
            if tx_data is None:
                # We cannot simply reassign the transaction to the different setting, as the old setting may be used for
                # the active or approved setting.
                for item in old_setting.recurring_transactions.all():
                    new_tx = copy.copy(item)
                    new_tx.id = None
                    new_tx.setting = setting
                    new_tx.save()
            else:
                # validate i_data fields
                for i_data in tx_data:
                    if 'enabled' not in i_data.keys():
                        raise ValidationError('Recurring transaction is missing enabled field.')
                RecurringTransaction.objects.bulk_create(
                    [RecurringTransaction(setting=setting,
                                          schedule=i_data['schedule'],
                                          enabled=i_data['enabled'],
                                          begin_date=i_data['begin_date'],
                                          growth=i_data['growth'],
                                          amount=i_data['amount'])
                     for i_data in tx_data]
                )

            try:
                goal.set_selected(setting)
            except CVE as verr:
                raise ValidationError(verr.message)

        return setting

    def create(self, validated_data):
        """
        Puts the passed settings into the 'selected_settings' field on the passed goal.
        """
        goal = validated_data.pop('goal')
        # MEtric group and hedge_fx are required on the model. I have no idea why I have to check it again here.
        metrics_data = validated_data.pop('metric_group', None)
        if metrics_data is None:
            raise ValidationError({"metric_group": "is required"})
        hedge_fx = validated_data.pop('hedge_fx', None)
        if hedge_fx is None:
            raise ValidationError({"hedge_fx": "is required"})
        tx_data = validated_data.pop('recurring_transactions', None)
        port_data = validated_data.pop('portfolio', None)
        with transaction.atomic():
            gid = metrics_data.get('id', None)
            if gid is None:
                metric_group = GoalMetricGroup.objects.create()
                metrics = metrics_data.get('metrics')
                mo = []
                for i_data in metrics:
                    if 'measured_val' in i_data:
                        raise ValidationError({"measured_val": "is read-only"})
                    mo.append(
                        GoalMetric(
                            group=metric_group,
                            type=i_data['type'],
                            feature=i_data.get('feature', None),
                            comparison=i_data['comparison'],
                            rebalance_type=i_data['rebalance_type'],
                            rebalance_thr=i_data['rebalance_thr'],
                            configured_val=i_data['configured_val'],
                        )
                    )
                GoalMetric.objects.bulk_create(mo)
            else:
                metric_group = GoalMetricGroup.objects.get(gid)

            setting = GoalSetting.objects.create(metric_group=metric_group,
                                                 # Target not required, so use default from model if omitted.
                                                 target=validated_data.get('target', 0),
                                                 completion=validated_data['completion'],
                                                 hedge_fx=hedge_fx,
                                                 rebalance=validated_data.get('rebalance', True),
                                                 )

            # Get the current portfolio statistics of the given weights if specified.
            if port_data is not None:
                port_items_data = port_data.pop('items')
                try:
                    er, stdev, idatas = current_stats_from_weights([(item['asset'].id,
                                                                     item['weight']) for item in port_items_data],
                                                                   DataProviderDjango())
                except Unsatisfiable as e:
                    raise ValidationError(e.msg)
                port = Portfolio.objects.create(setting=setting, er=er, stdev=stdev)
                PortfolioItem.objects.bulk_create([PortfolioItem(portfolio=port,
                                                                 asset=i_data['asset'],
                                                                 weight=i_data['weight'],
                                                                 volatility=idatas[i_data['asset'].id]) for i_data in port_items_data])

            if tx_data is not None:
                RecurringTransaction.objects.bulk_create(
                    [RecurringTransaction(setting=setting,
                                          schedule=i_data['schedule'],
                                          enabled=i_data['enabled'],
                                          begin_date=i_data['begin_date'],
                                          growth=i_data['growth'],
                                          amount=i_data['amount'])
                     for i_data in tx_data]
                )

            try:
                goal.set_selected(setting)
            except CVE as verr:
                raise ValidationError(verr.message)

        return setting


class GoalSettingStatelessSerializer(NoCreateModelSerializer, NoUpdateModelSerializer):
    """
    Creates a goal setting that has no database representation, but is linked to the real goal.
    We use the ModelSerializer to do all our field representation for us.
    """
    metric_group = GoalMetricGroupCreateSerializer()
    recurring_transactions = RecurringTransactionCreateSerializer(many=True)

    class Meta:
        model = GoalSetting
        fields = (
            'target',
            'completion',
            'hedge_fx',
            'metric_group',
            'recurring_transactions',
        )

    def save(self):
        raise NotImplementedError('Save is not a valid operation for a stateless serializer')

    @staticmethod
    def create_stateless(validated_data, goal):

        # Get the metrics
        metrics_data = validated_data.pop('metric_group')
        gid = metrics_data.get('id', None)
        if gid is None:
            mgroup = GoalMetricGroup()
            metrics = metrics_data.get('metrics')
            mo = []
            for ix, i_data in enumerate(metrics):
                compar = i_data.get('comparison', None)
                if compar is None:
                    emsg = "Metric {} in metrics list has no 'comparison' field, but it is required."
                    raise ValidationError(emsg.format(ix))
                metric = GoalMetric(group=mgroup,
                                    type=i_data['type'],
                                    feature=i_data.get('feature', None),
                                    comparison=i_data['comparison'],
                                    rebalance_type=i_data['rebalance_type'],
                                    rebalance_thr=i_data['rebalance_thr'],
                                    configured_val=i_data['configured_val'],
                                   )
                if metric.type == GoalMetric.METRIC_TYPE_PORTFOLIO_MIX and metric.feature is None:
                    emsg = "Metric {} in metrics list is a portfolio mix metric, but no feature is specified."
                    raise ValidationError(emsg.format(ix))
                mo.append(metric)

            class DummyGroup(object):
                class PseudoMgr:
                    @staticmethod
                    def all(): return mo
                metrics = PseudoMgr
            mtric_group = DummyGroup()
        else:
            mtric_group = GoalMetricGroup.objects.get(id=gid)

        goalt = goal

        # Currently unused
        tx_data = validated_data.pop('recurring_transactions')
        #RecurringTransaction.objects.bulk_create([RecurringTransaction(setting=setting, **i_data) for i_data in tx_data])

        class DummySettings(object):
            id = None
            goal = goalt
            target = validated_data.pop('target')
            completion = serializers.DateField().to_internal_value(validated_data.pop('completion'))
            metric_group = mtric_group

            def get_metrics_all(self):
                return self.metric_group.metrics.all()

            def __str__(self):
                return 'API Temp GoalSettings'

        return DummySettings()


class GoalSerializer(ReadOnlyModelSerializer):
    """
    This serializer is for READ-(GET) requests only. Currently this is enforced by the fact that it contains nested objects, but the fields
    'created' and 'cash_balance' should NEVER be updated by an API element.
    """
    class InvestedSerializer(serializers.Serializer):
        deposits = serializers.FloatField()
        withdrawals = serializers.FloatField()
        other = serializers.FloatField()
        net_pending = serializers.FloatField()

    class EarnedSerializer(serializers.Serializer):
        market_moves = serializers.FloatField()
        dividends = serializers.FloatField()
        fees = serializers.FloatField()

    # @property fields
    on_track = serializers.BooleanField()
    balance = serializers.FloatField(source='current_balance')
    earnings = serializers.FloatField(source='total_earnings')
    stock_balance = serializers.FloatField()
    bond_balance = serializers.FloatField()
    total_return = serializers.FloatField()
    invested = InvestedSerializer(source='investments')
    earned = EarnedSerializer(source='earnings')
    selected_settings = GoalSettingSerializer()

    class Meta:
        model = Goal


class GoalCreateSerializer(NoUpdateModelSerializer):
    """
    For write (POST/...) requests only
    """
    target = serializers.IntegerField()
    completion = serializers.DateField()
    initial_deposit = serializers.IntegerField(required=False)
    ethical = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Goal
        fields = (
            'account',
            'name',
            'type',
            'target',
            'completion',
            'initial_deposit',
            'ethical',
        )  # list fields explicitly

    def __init__(self, *args, **kwargs):
        super(GoalCreateSerializer, self).__init__(*args, **kwargs)

        # request-based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

        user = SupportRequest.target_user(request)

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

    def validate(self, attrs):
        if not attrs['account'].confirmed:
            raise ValidationError('Account is not verified.')
        return super(GoalCreateSerializer, self).validate(attrs)

    def create(self, validated_data):
        """
        Override the default create because we need to generate a portfolio.
        :param validated_data:
        :return: The created Goal
        """
        account = validated_data['account']

        data_provider = DataProviderDjango()
        execution_provider = ExecutionProviderDjango()
        idata = get_instruments(data_provider)

        with transaction.atomic():
            metric_group = GoalMetricGroup.objects.create(type=GoalMetricGroup.TYPE_CUSTOM)
            settings = GoalSetting.objects.create(
                target=validated_data['target'],
                completion=validated_data['completion'],
                hedge_fx=False,
                metric_group=metric_group,
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
            GoalMetric.objects.create(group=metric_group,
                                      type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                      comparison=GoalMetric.METRIC_COMPARISON_EXACTLY,
                                      rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                      rebalance_thr=0.05,
                                      configured_val=recommended_risk)
            if validated_data['ethical']:
                GoalMetric.objects.create(
                    group=metric_group,
                    type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                    feature=AssetFeatureValue.Standard.SRI_OTHER.get_object(),
                    comparison=GoalMetric.METRIC_COMPARISON_EXACTLY,
                    rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                    rebalance_thr=0.05,
                    configured_val=1  # Start with 100% ethical.
                )

            # Make sure the risk score assigned is appropriate for the goal.
            try:
                validate_risk_score(settings)
            except CVE as verr:
                raise ValidationError(verr.message)

            # Add the initial deposit if specified.
            initial_dep = validated_data.pop('initial_deposit', None)
            if initial_dep is not None:
                Transaction.objects.create(reason=Transaction.REASON_DEPOSIT,
                                           to_goal=goal,
                                           amount=initial_dep)

            # Calculate the optimised portfolio
            try:
                weights, er, stdev = calculate_portfolio(settings,
                                                         data_provider,
                                                         execution_provider,
                                                         idata)
                portfolio = Portfolio.objects.create(
                    setting=settings,
                    stdev=stdev,
                    er=er,
                )
                items = [PortfolioItem(portfolio=portfolio,
                                       asset=Ticker.objects.get(id=tid),
                                       weight=weight,
                                       volatility=idata[0].loc[tid, tid]) for tid, weight in weights.iteritems()]
                PortfolioItem.objects.bulk_create(items)
            except Unsatisfiable:
                # We detect when loading a goal in the allocation screen if there has been no portfolio created
                # and return a message to the user. It it perfectly reasonable for a goal to be created without a
                # portfolio.
                logger.exception("No suitable portfolio could be found. Leaving empty.")

        return goal


class GoalUpdateSerializer(NoCreateModelSerializer):
    """
    For write (PUT/...) requests only
    """
    # Only allow resetting the goal to active
    state = serializers.ChoiceField(required=False, choices=[Goal.State.ACTIVE.value])

    class Meta:
        model = Goal
        fields = (
            'name',
            'type',
            'portfolio_set',
            'state',
            'order',
        )  # list fields explicitly

    def __init__(self, *args, **kwargs):
        kwargs.pop('partial', None)
        super(GoalUpdateSerializer, self).__init__(*args, partial=True, **kwargs)

        # request based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

    @transaction.atomic
    def update(self, goal, validated_data):
        # Override the update method so we can make sure that only advisors can
        # update state, and only if the last state was ARCHIVE_REQUESTED
        request = self.context.get('request')
        new_state = validated_data.get('state', None)
        if new_state is not None and new_state != goal.state:
            if new_state != Goal.State.ACTIVE.value:
                raise PermissionDenied("The only state transition allowed is "
                                       "to {}".format(Goal.State.ACTIVE))
            if goal.state != Goal.State.ARCHIVE_REQUESTED.value:
                raise PermissionDenied(
                    "The only state transition allowed is from {}"
                    .format(Goal.State.ARCHIVE_REQUESTED)
                )
            sr = SupportRequest.get_current(request, as_obj=True)
            user, sr_id = (sr.user, sr.id) if sr else (request.user, None)
            # check helped user instead if support request is active
            if not user.is_advisor:
                raise PermissionDenied("Only an advisor can reactivate a goal")
            Event.REACTIVATE_GOAL.log('{} {}'.format(request.method,
                                                     request.path),
                                      user=request.user, obj=goal,
                                      support_request_id=sr_id)
        # Finally, if we pass the validation, allow the update
        return super(GoalUpdateSerializer, self).update(goal, validated_data)


class GoalGoalTypeListSerializer(ReadOnlyModelSerializer):
    """
    Experimental
    For read (GET) requests only
    """
    class Meta:
        model = GoalType
