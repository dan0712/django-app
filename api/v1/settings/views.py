from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route

from main.models import AssetClass, Ticker, GoalTypes
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisor, IsClient,
    IsAdvisorOrClient,
)

from . import serializers


class SettingsViewSet(ApiViewMixin, viewsets.GenericViewSet):
    """
    Experimental
    """
    #serializer_class = serializers.SettingsSerializer
    permission_classes = (
        IsAdvisorOrClient,
    )

    def list(self, request):
        # TODO: return all the settings
        raise NotImplementedError('Not implemented.')

    @list_route(methods=['get'], url_path='goal-types')
    def goal_types(self, request):
        goal_types = GoalTypes.objects.all().order_by('name')
        serializer = serializers.GoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='asset-classes')
    def asset_classes(self, request):
        asset_classes = AssetClass.objects.all().order_by('display_order', 'display_name')
        serializer = serializers.AssetClassListSerializer(asset_classes, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def tickers(self, request):
        tickers = Ticker.objects.all().order_by('ordering', 'display_name')
        serializer = serializers.TickerListSerializer(tickers, many=True)
        return Response(serializer.data)
