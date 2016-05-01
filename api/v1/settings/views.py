from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_extensions.mixins import NestedViewSetMixin

from main.models import AssetClass, Ticker, GoalType, AssetFeature, GoalMetric, RiskProfileGroup
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisorOrClient,
)

from . import serializers


class SettingsViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.GenericViewSet):
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
        goal_types = GoalType.objects.all().order_by('name')
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

    @list_route(methods=['get'], url_path='asset-features')
    def asset_features(self, request):
        res = [
            {
                "id": af.id,
                "name": af.name,
                "description": af.description,
                "values": [
                    {
                        "id": v.id,
                        "name": v.name,
                        "description": v.description
                    } for v in af.values.all()
                ]
            } for af in AssetFeature.objects.all()
        ]
        return Response(res)

    @list_route(methods=['get'])
    def constraint_comparisons(self, request):
        res = [
            {
                "id": key,
                "name": value
            } for key, value in dict(GoalMetric.comparisons).items()
        ]
        return Response(res)

    @list_route(methods=['get'], url_path='risk-profile-groups')
    def risk_profile_groups(self, request, **kwargs):
        risk_profile_groups = RiskProfileGroup.objects.all()
        serializer = serializers.RiskProfileGroupSerializer(risk_profile_groups, many=True)
        return Response(serializer.data)
