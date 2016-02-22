from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route

from api.v1.goals.serializers import PortfolioStatelessSerializer
from main.models import Goal, GoalTypes, TRANSACTION_TYPE_DEPOSIT
from portfolios.management.commands.portfolio_calculation import calculate_portfolio, get_instruments, Unsatisfiable, \
    calculate_portfolios
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisor,
    IsMyAdvisorCompany,
    IsAdvisorOrClient,
)

from . import serializers
#import .filters


class GoalViewSet(ApiViewMixin, viewsets.ModelViewSet):
    queryset = Goal.objects.all() \
        .select_related('account') \
        .select_related('active_settings') \
        .prefetch_related('active_settings__metrics')  
        # , 'approved_settings', 'selected_settings') \
        #.defer('account__data') \
    serializer_class = serializers.GoalSerializer
    serializer_response_class = serializers.GoalSerializer
    permission_classes = (
        IsAdvisorOrClient,
        #IsMyAdvisorCompany,
    )

    #filter_class = filters.GoalFilter
    filter_fields = ('name',)
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.action == 'list':
                return serializers.GoalListSerializer
            else:
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
            qs = qs.select_related()
            qs = qs.filter(archived=False)

        # show "permissioned" records only
        user = self.request.user

        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)

        if user.is_client:
            qs = qs.filter_by_client(user.client)

        return qs

    @list_route(methods=['get'])
    def types(self, request):
        goal_types = GoalTypes.objects.all().order_by('name')
        serializer = serializers.GoalGoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

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

    @detail_route(methods=['get', 'put'], url_path='selected-settings')
    def selected_settings(self, request, pk=None):
        goal = self.get_object()

        if request.method == 'GET':
            serializer = serializers.GoalSettingSerializer(goal.selected_settings)
            return Response(serializer.data)

        if request.method == 'PUT':
            serializer = serializers.GoalSettingCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            settings = serializer.save(goal=goal)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

        if user.advisor not in goal.account.advisors:
            raise PermissionDenied("You do not advise the client for this goal.")

        goal.approve_selected()
        serializer = serializers.GoalSettingSerializer(goal.approved_settings)

        return Response(serializer.data)

    @detail_route(methods=['post'], url_path='calculate-portfolio')
    def calculate_portfolio(self, request, pk=None):
        """
        Called to calculate a portfolio object for a set of supplied settings.
        """
        goal = self.get_object()

        # Create the settings from the request
        serializer = serializers.GoalSettingStatelessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings = serializer.create_stateless(serializer.validated_data, goal)

        # Calculate the portfolio
        idata = get_instruments()

        try:
            serializer = PortfolioStatelessSerializer(
                data=self.build_portfolio_data(idata, calculate_portfolio(settings, idata)),
                many=False)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Unsatisfiable as e:
            # TODO: Reformat this into a structured response..
            return Response("No portfolio could be found: {}".format(e))

    @detail_route(methods=['post'], url_path='calculate-all-portfolios')
    def calculate_all_portfolios(self, request, pk=None):
        """
        Called to calculate all the portfolio objects for 100 different risk scores for the supplied settings.
        """
        goal = self.get_object()

        # Create the settings from the request
        serializer = serializers.GoalSettingStatelessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settings = serializer.create_stateless(serializer.validated_data, goal)

        # Calculate the portfolio
        idata = get_instruments()

        try:
            serializer = PortfolioStatelessSerializer(
                data=[self.build_portfolio_data(idata, item) for item in calculate_portfolios(settings, idata)],
                many=True)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Unsatisfiable as e:
            # TODO: Reformat this into a structured response..
            return Response("No portfolio could be found: {}".format(e))

    @detail_route(methods=['post'])
    def deposit(self, request, pk=None):
        goal = self.get_object()
        serializer = serializers.TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(account=goal, type=TRANSACTION_TYPE_DEPOSIT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @staticmethod
    def build_portfolio_data(idata, item):
        if item is None:
            return None
        weights, variance, er = item
        return {
            'variance': variance,
            'er': er,
            'items': [
                {
                    'asset': idata[2].loc[sym, 'id'],
                    'weight': weight,
                    'volatility': idata[0].loc[sym, sym],
                } for sym, weight in weights.items()
            ]
        }
