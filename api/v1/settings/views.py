from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework_extensions.mixins import NestedViewSetMixin

from main.models import AssetClass, Ticker, GoalType, AssetFeature, GoalMetric, RiskProfileGroup, ACCOUNT_TYPES, \
    ActivityLog, AccountTypeRiskProfileGroup, PersonalData, EMPLOYMENT_STATUSES, ExternalAsset
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
        data = {
            'goal_types': self.goal_types(request).data,
            'account_types': self.account_types(request).data,
            'activity_types': self.activity_types(request).data,
            'asset_classes': self.asset_classes(request).data,
            'tickers': self.tickers(request).data,
            'asset_features': self.asset_features(request).data,
            'constraint_comparisons': self.constraint_comparisons(request).data,
            'risk_profile_groups': self.risk_profile_groups(request).data,
            'civil_statuses': [{"id": status.value, "name": status.name} for status in PersonalData.CivilStatus],
            'employment_statuses': [{"id": sid, "name": name} for sid, name in EMPLOYMENT_STATUSES],
            'external_asset_types': [{"id": choice[0], "name": choice[1]} for choice in ExternalAsset.Type.choices()],
        }
        return Response(data)

    @list_route(methods=['get'], url_path='goal-types')
    def goal_types(self, request):
        goal_types = GoalType.objects.all().order_by('name')
        serializer = serializers.GoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='account-types')
    def account_types(self, request):
        maps = dict(AccountTypeRiskProfileGroup.objects.all().values_list('account_type', 'risk_profile_group__id'))
        res = []
        for key, value in ACCOUNT_TYPES:
            rpg = maps.get(key, None)
            if rpg is None:
                raise Exception(
                    "Configuration Error: AccountType: {}({}) has no default Risk Profile Group.".format(value, key)
                )
            res.append({
                "id": key,
                "name": value,
                "default_risk_profile_group": rpg,
            })

        return Response(res)

    @list_route(methods=['get'], url_path='activity-types')
    def activity_types(self, request):
        activity_types = ActivityLog.objects.all().order_by('name')
        serializer = serializers.ActivityLogSerializer(activity_types, many=True)
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
    def risk_profile_groups(self, request):
        risk_profile_groups = RiskProfileGroup.objects.all()
        serializer = serializers.RiskProfileGroupSerializer(risk_profile_groups, many=True)
        return Response(serializer.data)
