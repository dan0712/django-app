import datetime
import ujson

from django.db import transaction
from django.db.models.query_utils import Q
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route

from api.v1.exceptions import APIInvalidStateError
from api.v1.goals.serializers import PortfolioStatelessSerializer
from main.event import Event
from main.models import Goal, GoalType, Transaction, HistoricalBalance
from portfolios.management.commands.portfolio_calculation import calculate_portfolio, Unsatisfiable, \
    calculate_portfolios
from portfolios.management.commands.risk_profiler import recommend_ttl_risks
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisor,
    IsMyAdvisorCompany,
    IsAdvisorOrClient,
)

from . import serializers
#import .filters

EPOCH_DT = datetime.datetime.utcfromtimestamp(0).date()


def check_state(current, required):
    if isinstance(required, (list, tuple)):
        if current not in required:
            raise APIInvalidStateError(current, required)
    elif current != required:
        raise APIInvalidStateError(current, required)


class GoalViewSet(ApiViewMixin, viewsets.ModelViewSet):
    queryset = Goal.objects.all() \
        .select_related('account') \
        .select_related('selected_settings') \
        .prefetch_related('selected_settings__metric_group')
        # , 'approved_settings', 'selected_settings') \
        #.defer('account__data') \
    serializer_class = serializers.GoalSerializer
    # We don't want pagination on goals for now, as the UI can't handle it. We can add it back of we need to.
    pagination_class = None
    serializer_response_class = serializers.GoalSerializer
    permission_classes = (
        IsAdvisorOrClient,
        #IsMyAdvisorCompany,
    )

    #filter_class = filters.GoalFilter
    filter_fields = ('name',)
    search_fields = ('name',)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Override this method as we don't want to actually delete the goal, just disable it.
        :param instance: The goal to disable
        :return: None
        """
        goal = self.get_object()
        # If I'm an adviser or the goal is unsupervised, archive the goal immediately.
        if not goal.supervised or self.request.user.is_advisor:
            check_state(Goal.State(goal.state), [Goal.State.ACTIVE, Goal.State.ARCHIVE_REQUESTED])
            Event.ARCHIVE_GOAL.log('{} {}'.format(self.request.method, self.request.path),
                                   user=self.request.user,
                                   obj=goal)
            # Set the state to archive requested, as the call to archive() requires it.
            goal.state = Goal.State.ARCHIVE_REQUESTED.value
            goal.archive()
        else:
            check_state(Goal.State(goal.state), Goal.State.ACTIVE)
            Event.ARCHIVE_GOAL_REQUESTED.log('{} {}'.format(self.request.method, self.request.path),
                                             user=self.request.user,
                                             obj=goal)
            # Flag the goal as archive requested.
            goal.state = Goal.State.ARCHIVE_REQUESTED.value
            goal.save()
        return Response(serializers.GoalSerializer(goal).data)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.GoalSerializer
        else:
            if self.action == 'create':
                return serializers.GoalCreateSerializer
            else:
                return serializers.GoalUpdateSerializer

    def get_queryset(self):
        qs = self.queryset

        # hide "slow" fields for list view
        if self.action == 'list':
            qs = qs.prefetch_related()
            qs = qs.select_related('selected_settings')
            qs = qs.exclude(state=Goal.State.ARCHIVED.value)

        # show "permissioned" records only
        user = self.request.user

        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)

        if user.is_client:
            qs = qs.filter_by_client(user.client)

        return qs

    @list_route(methods=['get'])
    def types(self, request):
        goal_types = GoalType.objects.all().order_by('name')
        serializer = serializers.GoalGoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def states(self, request):
        return Response(Goal.State.choices())

    @detail_route(methods=['get'])
    def positions(self, request, pk=None):
        goal = self.get_object()

        positions = goal.positions.all()
        serializer = serializers.GoalPositionListSerializer(positions, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='selected-portfolio')
    def selected_portfolio(self, request, pk=None):
        goal = self.get_object()
        portfolio = goal.selected_settings.portfolio
        serializer = serializers.PortfolioSerializer(portfolio)
        return Response(serializer.data)

    @detail_route(methods=['get', 'post', 'put'], url_path='selected-settings')
    def selected_settings(self, request, pk=None):
        goal = self.get_object()

        if request.method == 'GET':
            serializer = serializers.GoalSettingSerializer(goal.selected_settings)
            return Response(serializer.data)

        if request.method == 'POST':
            check_state(Goal.State(goal.state), Goal.State.ACTIVE)
            serializer = serializers.GoalSettingWritableSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            settings = serializer.save(goal=goal)
            headers = self.get_success_headers(serializer.data)
            serializer = serializers.GoalSettingSerializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

        elif request.method == 'PUT':
            check_state(Goal.State(goal.state), Goal.State.ACTIVE)
            setting = goal.selected_settings
            serializer = serializers.GoalSettingWritableSerializer(setting, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            settings = serializer.save(goal=goal)
            headers = self.get_success_headers(serializer.data)
            # We use a different serializer to send the new settings, as the update serializer is limited.
            serializer = serializers.GoalSettingSerializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @detail_route(methods=['get'], url_path='approved-settings')
    def approved_settings(self, request, pk=None):
        goal = self.get_object()
        serializer = serializers.GoalSettingSerializer(goal.approved_settings)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='active-settings')
    def active_settings(self, request, pk=None):
        """
        Handy for backups....
        """
        goal = self.get_object()
        serializer = serializers.GoalSettingSerializer(goal.active_settings)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='approve-selected')
    def approve_selected(self, request, pk=None):
        """
        Called to make the currently selected settings approved by the advisor,
        and ready to be activated next time the account is processed (rebalance).
        """
        user = self.request.user
        if not user.is_advisor:
            raise PermissionDenied('Only an advisor can approve selections.')

        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)

        if user.advisor not in goal.account.advisors:
            raise PermissionDenied("You do not advise the client for this goal.")

        goal.approve_selected()
        serializer = serializers.GoalSettingSerializer(goal.approved_settings)

        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='calculate-portfolio')
    def calculate_portfolio(self, request, pk=None):
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
            data = self.build_portfolio_data(calculate_portfolio(settings))
            return Response(data)
        except Unsatisfiable as e:
            rdata = {'reason': "No portfolio could be found: {}".format(e)}
            if e.req_funds is not None:
                rdata['req_funds'] = e.req_funds

            return Response({'error': rdata}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], url_path='calculate-all-portfolios')
    def calculate_all_portfolios(self, request, pk=None):
        """
        Called to calculate all the portfolio objects for 100 different risk scores for the supplied settings.
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

        # Create the settings from the dict
        serializer = serializers.GoalSettingStatelessSerializer(data=setting)
        serializer.is_valid(raise_exception=True)
        settings = serializer.create_stateless(serializer.validated_data, goal)

        # Calculate the portfolio
        try:
            data = [self.build_portfolio_data(item[1], item[0]) for item in calculate_portfolios(settings)]
            return Response(data)
        except Unsatisfiable as e:
            rdata = {'reason': "No portfolio could be found: {}".format(e)}

            if e.req_funds is not None:
                rdata['req_funds'] = e.req_funds

            return Response({'error': rdata}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def deposit(self, request, pk=None):
        goal = self.get_object()

        check_state(Goal.State(goal.state), Goal.State.ACTIVE)

        serializer = serializers.TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(to_goal=goal, reason=Transaction.REASON_DEPOSIT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['get'], url_path='recommended-risk-scores')
    def recommended_risk_scores(self, request, pk=None):
        setting = self.get_object().selected_settings
        years = request.query_params.get('years', None)
        if not years:
            raise ValidationError("Query parameter 'years' must be specified and non-zero")
        try:
            years = int(years)
        except ValueError:
            raise ValidationError("Query parameter 'years' must be an integer")
        return Response(recommend_ttl_risks(setting, years))

    @detail_route(methods=['get'], url_path='cash-flow')
    def cash_flow(self, request, pk=None):
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
        return Response([((tx[1].date() - EPOCH_DT).days, tx[2] if tx[0] else -tx[2]) for tx in txs])

    @detail_route(methods=['get'], url_path='balance-history')
    def balance_history(self, request, pk=None):
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
