from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route

from main.models import Goal, GoalTypes, GoalSetting
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

