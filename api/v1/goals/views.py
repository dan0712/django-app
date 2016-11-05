import decimal
import logging
import ujson
from collections import defaultdict

import operator
import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied, \
    ValidationError
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.exceptions import APIInvalidStateError, SystemConstraintError
from api.v1.utils import activity
from api.v1.views import ReadOnlyApiViewMixin
from common.constants import EPOCH_DT, EPOCH_TM
from common.utils import dt2ed
from main.event import Event
from main.models import DailyPrice, Goal, GoalType, HistoricalBalance, Ticker, Transaction, GoalSetting
from main.risk_profiler import risk_data
from portfolios.calculation import Unsatisfiable, \
    calculate_portfolio, calculate_portfolios, current_stats_from_weights
from portfolios.providers.execution.django import ExecutionProviderDjango
from portfolios.providers.data.django import DataProviderDjango
from support.models import SupportRequest
from . import serializers
from ..permissions import IsAdvisorOrClient
from ..views import ApiViewMixin

# Make unsafe float operations with decimal fail
decimal.getcontext().traps[decimal.FloatOperation] = True

logger = logging.getLogger('api.v1.goals.views')


def check_state(current, required):
    if isinstance(required, (list, tuple)):
        if current not in required:
            raise APIInvalidStateError(current, required)
    elif current != required:
        raise APIInvalidStateError(current, required)


class GoalViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    # We define the queryset because our get_queryset calls super.
    queryset = Goal.objects.all() \
        .select_related('account') \
        .select_related('selected_settings') \
        .prefetch_related('selected_settings__metric_group')
        # , 'approved_settings', 'selected_settings') \
        # .defer('account__data') \

    # We don't want pagination on goals for now, as the UI can't handle it. We can add it back of we need to.
    pagination_class = None
    permission_classes = (
        IsAdvisorOrClient,
        #IsMyAdvisorCompany,
    )

    #filter_class = filters.GoalFilter
    filter_fields = ('name',)
    search_fields = ('name',)

    # We set the response serializer because for the 'create' methods, we have custom fields,
    # and when we return the response, we want to use the full goal serializer. See api/v1/views.py
    serializer_response_class = serializers.GoalSerializer

    # We can never delete goals from the API. Only archive them.
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.GoalSerializer
        else:
            if self.action == 'create':
                return serializers.GoalCreateSerializer
            else:
                return serializers.GoalUpdateSerializer

    def get_queryset(self):
        qs = super(GoalViewSet, self).get_queryset()

        # hide "slow" fields for list view
        if self.action == 'list':
            qs = qs.prefetch_related()
            qs = qs.select_related('selected_settings')
            qs = qs.exclude(state=Goal.State.ARCHIVED.value)

        # show "permissioned" records only
        user = SupportRequest.target_user(self.request)
        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)
        elif user.is_client:
            qs = qs.filter_by_client(user.client)
        else:
            raise PermissionDenied('Only Advisors or Clients are allowed '
                                   'to access goals.')

        return qs

    @list_route(methods=['get'])
    def types(self, request, **kwargs):
        goal_types = GoalType.objects.all().order_by('order')
        serializer = serializers.GoalGoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def states(self, request, **kwargs):
        return Response(Goal.State.choices())

    @detail_route(methods=['put'])
    @transaction.atomic
    # Atomic so the log doesn't get written if the whole thing rolls back.
    def archive(self, request, pk=None, **kwargs):
        """
        Override this method as we don't want to actually delete the goal,
        just disable it.
        :param instance: The goal to disable
        :return: None
        """
        goal = self.get_object()
        # If I'm an adviser or the goal is unsupervised,
        # archive the goal immediately.
        sr = SupportRequest.get_current(request, as_obj=True)
        # check helped user instead if support request is active
        user, sr_id = (sr.user, sr.id) if sr else (request.user, None)
        if not goal.account.supervised or user.is_advisor:
            check_state(Goal.State(goal.state),
                        [Goal.State.ACTIVE, Goal.State.ARCHIVE_REQUESTED])
            Event.ARCHIVE_GOAL.log('{} {}'.format(request.method,
                                                  request.path),
                                   user=request.user, obj=goal,
                                   support_request_id=sr_id)
            # Set the state to archive requested,
            # as the call to archive() requires it.
            goal.state = Goal.State.ARCHIVE_REQUESTED.value
            goal.archive()
        else:
            # I'm a client with a supervised goal, just change the status to
            # ARCHIVE_REQUESTED, and add a notification
            check_state(Goal.State(goal.state), Goal.State.ACTIVE)
            Event.ARCHIVE_GOAL_REQUESTED.log('{} {}'.format(request.method,
                                                            request.path),
                                             user=request.user, obj=goal,
                                             support_request_id=sr_id)
            # Flag the goal as archive requested.
            goal.state = Goal.State.ARCHIVE_REQUESTED.value
            # TODO: Add a notification to the advisor that the goal is archive requested.
            goal.save()
        return Response(serializers.GoalSerializer(goal).data)

    @detail_route(methods=['get'])
    def positions(self, request, pk=None, **kwargs):
        goal = self.get_object()
        positions = goal.get_positions_all()
        return Response([{'ticker': item['ticker_id'], 'quantity': item['quantity']} for item in positions])

    @detail_route(methods=['get'])
    def activity(self, request, pk=None, **kwargs):
        goal = self.get_object()
        return activity.get(request, goal)

    @detail_route(methods=['get'], url_path='selected-portfolio')
    def selected_portfolio(self, request, pk=None, **kwargs):
        goal = self.get_object()
        portfolio = getattr(goal.selected_settings, 'portfolio', None)
        serializer = serializers.PortfolioSerializer(portfolio)
        return Response(serializer.data)

    @detail_route(methods=['get', 'post', 'put'], url_path='selected-settings')
    def selected_settings(self, request, pk=None, **kwargs):
        goal = self.get_object()

        if request.method == 'GET':
            serializer = serializers.GoalSettingSerializer(goal.selected_settings)
            return Response(serializer.data)

        with transaction.atomic():  # So both the log and change get committed.
            sr_id = SupportRequest.get_current(request)
            if request.method == 'POST':
                check_state(Goal.State(goal.state), Goal.State.ACTIVE)
                serializer = serializers.GoalSettingWritableSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                event = Event.SET_SELECTED_SETTINGS.log('{} {}'.format(self.request.method, self.request.path),
                                                        request.data,
                                                        user=request.user,
                                                        obj=goal,
                                                        support_request_id=sr_id)
                # Write any event memo for the event. All the details are wrapped by the serializer.
                serializer.write_memo(event)
                settings = serializer.save(goal=goal)
                # We use the read-only serializer to send the settings object, not the update serializer.
                serializer = serializers.GoalSettingSerializer(settings)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

            elif request.method == 'PUT':
                check_state(Goal.State(goal.state), Goal.State.ACTIVE)
                settings = goal.selected_settings
                event = Event.UPDATE_SELECTED_SETTINGS.log('{} {}'.format(self.request.method, self.request.path),
                                                           request.data,
                                                           user=request.user,
                                                           obj=goal,
                                                           support_request_id=sr_id)
                serializer = serializers.GoalSettingWritableSerializer(settings, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                # Write any event memo for the event. All the details are wrapped by the serializer.
                serializer.write_memo(event)
                settings = serializer.save(goal=goal)
                # We use the read-only serializer to send the settings object, not the update serializer.
                serializer = serializers.GoalSettingSerializer(settings)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @detail_route(methods=['get'], url_path='settings')
    def settings_by_id(self, request, pk=None, **kwargs):
        try:
            settings = GoalSetting.objects.get(pk=pk)
        except:
            return Response('Settings not found', status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.GoalSettingSerializer(settings)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='approved-settings')
    def approved_settings(self, request, pk=None, **kwargs):
        goal = self.get_object()
        serializer = serializers.GoalSettingSerializer(goal.approved_settings)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='active-settings')
    def active_settings(self, request, pk=None, **kwargs):
        """
        Handy for backups....
        """
        goal = self.get_object()
        serializer = serializers.GoalSettingSerializer(goal.active_settings)
        return Response(serializer.data)

    # Atomic so both the log and the change have to be written.
    @transaction.atomic
    @detail_route(methods=['put'], url_path='approve-selected')
    def approve_selected(self, request, pk=None, **kwargs):
        """
        Called to make the currently selected settings approved by the advisor,
        ready to be activated next time the account is processed (rebalance).
        """
        sr = SupportRequest.get_current(request, as_obj=True)
        # check helped user instead if support request is active
        user, sr_id = (sr.user, sr.id) if sr else (request.user, None)
        if not user.is_advisor:
            raise PermissionDenied('Only an advisor can approve selections.')

        goal = self.get_object()
        check_state(Goal.State(goal.state), Goal.State.ACTIVE)
        Event.APPROVE_SELECTED_SETTINGS.log('{} {}'.format(request.method,
                                                           request.path),
                                            user=request.user,
                                            obj=goal,
                                            support_request_id=sr_id)
        goal.approve_selected()

        serializer = serializers.GoalSettingSerializer(goal.approved_settings)

        return Response(serializer.data)

    # Atomic so both the log and the change have to be written.
    @transaction.atomic
    @detail_route(methods=['put'], url_path='revert-selected')
    def revert_selected(self, request, pk=None, **kwargs):
        """
        Called to revert the current selected-settings to the approved-settings
        Returns a validation error if there is no approved-settings.
        """
        goal = self.get_object()
        check_state(Goal.State(goal.state), Goal.State.ACTIVE)
        if not goal.approved_settings:
            raise ValidationError("No settings have yet been approved for "
                                  "this Goal, cannot revert to last approved.")
        sr_id = SupportRequest.get_current(request)
        Event.REVERT_SELECTED_SETTINGS.log('{} {}'.format(request.method,
                                                          request.path),
                                           user=request.user,
                                           obj=goal,
                                           support_request_id=sr_id)
        goal.revert_selected()
        serializer = serializers.GoalSettingSerializer(goal.selected_settings)

        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='calculate-performance')
    def calculate_performance(self, request, pk=None, **kwargs):
        port_items_str = request.query_params.get('items', None)
        errstr = "Query parameter 'items' must be specified and a valid JSON string [[asset_id, weight], ...]"
        if not port_items_str:
            raise ValidationError(errstr)
        try:
            port_items = ujson.loads(port_items_str)
        except ValueError:
            raise ValidationError(errstr)
        total_weight = sum([item[1] for item in port_items])
        if total_weight > 1.0001:
            raise ValidationError("Sum of item weights must be less than or equal to 1")
        try:
            er, stdev, _ = current_stats_from_weights(port_items, DataProviderDjango())
        except Unsatisfiable as e:
            raise ValidationError(e.msg)
        return Response({'er': er, 'stdev': stdev})

    @detail_route(methods=['get'], url_path='calculate-portfolio')
    def calculate_portfolio(self, request, pk=None, **kwargs):
        """
        Called to calculate a portfolio object for a set of supplied settings.
        """
        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)

        setting_str = request.query_params.get('setting', None)
        if not setting_str:
            raise ValidationError("Query parameter 'setting' must be specified and a valid JSON string")
        try:
            setting = ujson.loads(setting_str)
        except ValueError:
            raise ValidationError("Query parameter 'setting' must be a valid json string")

        # Create the settings object from the dict
        serializer = serializers.GoalSettingStatelessSerializer(data=setting)
        serializer.is_valid(raise_exception=True)
        settings = serializer.create_stateless(serializer.validated_data, goal)

        try:
            data = self.build_portfolio_data(calculate_portfolio(settings=settings,
                                                                 data_provider=DataProviderDjango(),
                                                                 execution_provider=ExecutionProviderDjango()))
            return Response(data)
        except Unsatisfiable as e:
            rdata = {'reason': "No portfolio could be found: {}".format(e)}
            if e.req_funds is not None:
                rdata['req_funds'] = e.req_funds

            return Response({'error': rdata}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], url_path='calculate-all-portfolios')
    def calculate_all_portfolios(self, request, pk=None, **kwargs):
        """
        Called to calculate all the portfolio objects for 100 different risk scores for the supplied settings.
        """
        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)

        setting_str = request.query_params.get('setting', None)
        if not setting_str:
            logger.debug('setting parameter missing from calculate_all_portfolios query')
            raise ValidationError("Query parameter 'setting' must be specified and a valid JSON string")
        try:
            setting = ujson.loads(setting_str)
        except ValueError:
            logger.debug('setting parameter for calculate_all_portfolios query not valid json')
            raise ValidationError("Query parameter 'setting' must be a valid json string")

        # Create the settings from the dict
        serializer = serializers.GoalSettingStatelessSerializer(data=setting)
        serializer.is_valid(raise_exception=True)
        settings = serializer.create_stateless(serializer.validated_data, goal)

        # Calculate the portfolio
        try:
            data_provider = DataProviderDjango()
            execution_provider = ExecutionProviderDjango()
            data = [self.build_portfolio_data(item[1], item[0])
                    for item in calculate_portfolios(setting=settings,
                                                     data_provider=data_provider,
                                                     execution_provider=execution_provider)]
            return Response(data)
        except Unsatisfiable as e:
            rdata = {'reason': "No portfolio could be found: {}".format(e)}

            if e.req_funds is not None:
                rdata['req_funds'] = e.req_funds

            return Response({'error': rdata}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def deposit(self, request, pk=None, **kwargs):
        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)
        sr_id = SupportRequest.get_current(request)
        Event.GOAL_DEPOSIT.log('{} {}'.format(request.method, request.path),
                               request.data,
                               user=request.user, obj=goal,
                               support_request_id=sr_id)
        serializer = serializers.TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(to_goal=goal, reason=Transaction.REASON_DEPOSIT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @detail_route(methods=['post'])
    def withdraw(self, request, pk=None, **kwargs):
        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)
        sr_id = SupportRequest.get_current(request)
        Event.GOAL_WITHDRAWAL.log('{} {}'.format(request.method, request.path),
                                  request.data,
                                  user=request.user,
                                  obj=goal,
                                  support_request_id=sr_id)
        serializer = serializers.TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Make sure the total amount for the goal is larger than the pending withdrawal amount.
        if goal.current_balance + 0.0000001 < serializer.validated_data['amount']:
            emsg = "Goal's current balance: {} is less than the desired withdrawal amount: {}"
            raise SystemConstraintError(emsg.format(goal.current_balance, serializer.validated_data['amount']))
        serializer.save(from_goal=goal, reason=Transaction.REASON_WITHDRAWAL)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['get'], url_path='risk-score-data')
    def recommended_risk_scores(self, request, pk=None, **kwargs):
        setting = self.get_object().selected_settings
        return Response(risk_data(setting))

    @detail_route(methods=['get'], url_path='cash-flow')
    def cash_flow(self, request, pk=None, **kwargs):
        """
        Returns all the cash-flow events for this goal.
        :param request:
        :param pk:
        :return:
        """
        # Get the goal even though we don't need it (we could ust use the pk)
        # so we can ensure we have permission to do so.
        goal = self.get_object()
        txs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                         status=Transaction.STATUS_EXECUTED,
                                         reason__in=Transaction.CASH_FLOW_REASONS)
        txs = txs.order_by('executed').values_list('to_goal', 'executed', 'amount')
        return Response([(dt2ed(tx[1]), tx[2] if tx[0] else -tx[2]) for tx in txs])

    @detail_route(methods=['get'], url_path='balance-history')
    def balance_history(self, request, pk=None, **kwargs):
        """
        Returns the balance history for this goal.
        :param request: The web request
        :param pk: THe id of the goal
        :return: A django rest framework response object
        """
        # Get the goal even though we don't need it (we could ust use the pk)
        # so we can ensure we have permission to do so.
        goal = self.get_object()
        rows = HistoricalBalance.objects.filter(goal=goal).order_by('date').values_list('date', 'balance')
        return Response([((row[0] - EPOCH_DT).days, row[1]) for row in rows])

    @detail_route(methods=['get'], url_path='pending-transfers')
    def pending_transfers(self, request, pk=None, **kwargs):
        # Get the goal even though we don't need it (we could just use the pk)
        # so we can ensure we have permission to do so, as permissions are checked in get_object()
        goal = self.get_object()

        qs = goal.pending_transactions.filter(reason__in=[Transaction.REASON_DEPOSIT, Transaction.REASON_WITHDRAWAL])\

        values = qs.order_by('-created').values_list('id', 'created', 'amount', 'to_goal')
        return Response([{"id": item[0],
                          "time": int((timezone.make_naive(item[1], timezone.utc) - EPOCH_TM).total_seconds()),
                          "amount": item[2] * (1 if item[3] else -1)} for item in values])

    @detail_route(methods=['get'], url_path='performance-history')
    def performance_history(self, request, pk=None, **kwargs):
        """
        Returns the performance history for this goal. I.e. The raw performance given the periods of stocks held.
        This doesn't consider the price the stocks were actually bought or sold, just the movement of the market prices
        considering the volumes held by the goal over time. I.e. Execution costs (fees, spread etc) are not considered.
        :param request: The web request
        :param pk: The id of the goal
        :return: A django rest framework response object with date, perf tuples
                 eg. [[112234232,0.00312],[112234233,-0.00115], ...]
        """
        # Get the goal even though we don't need it (we could just use the pk)
        # so we can ensure we have permission to do so.
        goal = self.get_object()

        # - Get all the transaction with this goal involved that are of reason 'Execution'.
        #   We want the volume, ticker id, date ordered by date. [(date, {ticker: vol}, ...]
        qs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                        reason=Transaction.REASON_EXECUTION).order_by('executed')
        txs = qs.values_list('execution_distribution__execution__executed',
                             'execution_distribution__execution__asset__id',
                             'execution_distribution__volume')
        ts = []
        entry = (None,)
        aids = set()
        # If there were no transactions, there can be no performance
        if len(txs) == 0:
            return Response([])

        # Because executions are stored with timezone, but other things are just as date, we need to make datetimes
        # naive before doing date arithmetic on them.
        bd = timezone.make_naive(txs[0][0]).date()
        ed = timezone.make_naive(timezone.now()).date()
        for tx in txs:
            aids.add(tx[1])
            txd = timezone.make_naive(tx[0]).date()
            if txd == entry[0]:
                entry[1][tx[1]] += tx[2]
            else:
                if entry[0] is not None:
                    ts.append(entry)
                entry = (txd, defaultdict(int))
                entry[1][tx[1]] = tx[2]
        ts.append(entry)

        # - Get the time-series of prices for each instrument from the first transaction date until now.
        #   Fill empty dates with previous value [(date, {ticker: price}, ...]
        pqs = DailyPrice.objects.filter(date__range=(bd, ed),
                                        instrument_content_type=ContentType.objects.get_for_model(Ticker).id,
                                        instrument_object_id__in=aids)
        prices = pqs.to_timeseries(fieldnames=['price', 'date', 'instrument_object_id'],
                                   index='date',
                                   storage='long',
                                   pivot_columns='instrument_object_id',
                                   values='price')
        # Remove negative prices and fill missing values
        # We replace negs with None so they are interpolated.
        prices[prices <= 0] = None
        prices = prices.reindex(pd.date_range(bd, ed), method='ffill').fillna(method='bfill')

        # For each day, calculate the performance
        piter = prices.itertuples()
        res = []
        # Process the first day - it's special
        row = next(piter)
        p_m1 = row[1:]
        vols_m1 = [0] * len(prices.columns)
        tidlocs = {tid: ix for ix, tid in enumerate(prices.columns)}
        for tid, vd in ts.pop(0)[1].items():
            vols_m1[tidlocs[tid]] += vd
        res.append((dt2ed(row[0]), 0))  # First day has no performance as there wasn't a move
        # Process the rest
        for row in piter:
            # row[0] (a datetime) is a naive timestamp, so we don't need to convert it
            if ts and row[0].date() == ts[0][0]:
                vols = vols_m1.copy()
                dtrans = ts.pop(0)[1]  # The transactions for the current processed day.
                for tid, vd in dtrans.items():
                    vols[tidlocs[tid]] += vd
                # The exposed assets for the day. These are the assets we know for sure were exposed for the move.
                pvol = list(map(min, vols, vols_m1))
            else:
                vols = vols_m1
                pvol = vols
            pdelta = list(map(operator.sub, row[1:], p_m1))  # The change in price from yesterday
            impact = sum(map(operator.mul, pvol, pdelta))  # The total portfolio impact due to price moves for exposed assets.
            b_m1 = sum(map(operator.mul, pvol, p_m1))  # The total portfolio value yesterday for the exposed assets.
            perf = 0 if b_m1 == 0 else impact / b_m1
            # row[0] (a datetime) is a naive timestamp, so we don't need to convert it
            res.append((dt2ed(row[0]), decimal.Decimal.from_float(perf).quantize(decimal.Decimal('1.000000'))))
            p_m1 = row[1:]
            vols_m1 = vols[:]

        return Response(res)

    @staticmethod
    def build_portfolio_data(item, risk_score=None):
        if item is None:
            return None
        weights, er, stdev = item
        res = {
            'stdev': stdev,
            'er': er,
            'items': [
                {
                    'asset': tid,
                    'weight': weight
                } for tid, weight in weights.iteritems()
            ]
        }
        if risk_score is None:
            return res
        else:
            return {'risk_score': risk_score, 'portfolio': res}


class GoalSettingViewSet(ReadOnlyApiViewMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (
        IsAdvisorOrClient,
    )

    serializer_class = serializers.GoalSettingSerializer

    def retrieve(self, request, pk=None, **kwargs):
        settings = GoalSetting.objects.filter(pk=pk).first()
        if not settings or not (request.user.id == settings.goal.account.primary_owner.user.id or
                request.user.id == settings.goal.account.primary_owner.advisor.user.id or
                (settings.goal.account.account_group and (
                    request.user.id == settings.goal.account.account_group.advisor.user.id or
                    settings.goal.account.account_group.secondary_advisors.filter(user__id=request.user.id).exists()))):
            # Don't tell unauthorized people it exists, be stealth and just tell them it doesn't exist.
            return Response('Settings not found', status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(settings)
        return Response(serializer.data)
