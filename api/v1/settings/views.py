from django.conf import settings
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from client.models import AccountTypeRiskProfileGroup, RiskProfileGroup
from main import constants, models
from main.abstract import PersonalData
from ..goals.serializers import GoalSettingSerializer
from . import serializers
from ..permissions import IsAdvisorOrClient
from ..views import ApiViewMixin
from client import models as client_models
from retiresmartz import models as retirement_models


class SettingsViewSet(ApiViewMixin, NestedViewSetMixin, GenericViewSet):
    """
    Experimental
    """
    serializer_class = GoalSettingSerializer
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
            'constraint_comparisons':
                self.constraint_comparisons(request).data,
            'risk_profile_groups': self.risk_profile_groups(request).data,
            'civil_statuses': self.civil_statuses(request).data,
            'employment_statuses': self.employment_statuses(request).data,
            'external_asset_types': self.external_asset_types(request).data,
            'investor_risk_categories': self.investor_risk_categories(request).data,
            'retirement_saving_categories': self.retirement_saving_categories(request).data,
            'retirement_expense_categories': self.retirement_expense_categories(request).data,
            'retirement_housing_categories': self.retirement_housing_categories(request).data,
            'retirement_lifestyle_categories': self.retirement_lifestyle_categories(request).data,
            'retirement_lifestyles': self.retirement_lifestyles(request).data,
            'constants': self.constants(request).data,
        }
        return Response(data)

    @list_route(methods=['get'], url_path='goal-types')
    def goal_types(self, request):
        goal_types = models.GoalType.objects.order_by('name')
        serializer = serializers.GoalTypeListSerializer(goal_types, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='account-types')
    def account_types(self, request):
        res = []
        for key, value in constants.ACCOUNT_TYPES:
            res.append({
                "id": key,
                "name": value
            })

        return Response(res)

    @list_route(methods=['get'], url_path='activity-types')
    def activity_types(self, request):
        activity_types = models.ActivityLog.objects.order_by('name')
        serializer = serializers.ActivityLogSerializer(activity_types,
                                                       many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='asset-classes')
    def asset_classes(self, request):
        asset_classes = models.AssetClass.objects.order_by('display_order',
                                                           'display_name')
        serializer = serializers.AssetClassListSerializer(asset_classes,
                                                          many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def tickers(self, request):
        tickers = models.Ticker.objects.order_by('ordering', 'display_name')
        serializer = serializers.TickerListSerializer(tickers, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='asset-features')
    def asset_features(self, request):
        res = [{
                   "id": af.id,
                   "name": af.name,
                   "description": af.description,
                   "values": [{
                                  "id": v.id,
                                  "name": v.name,
                                  "description": v.description
                              } for v in af.values.all()]
               } for af in models.AssetFeature.objects.all()]
        return Response(res)

    @list_route(methods=['get'])
    def constraint_comparisons(self, request):
        comparisons = models.GoalMetric.comparisons
        return Response([{
                             "id": key,
                             "name": value
                         } for key, value in comparisons.items()])

    @list_route(methods=['get'], url_path='risk-profile-groups', permission_classes=[IsAuthenticated])
    def risk_profile_groups(self, request):
        groups = RiskProfileGroup.objects.all()
        serializer = serializers.RiskProfileGroupSerializer(groups, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def civil_statuses(self, request):
        return Response([{"id": status.value, "name": status.name}
                         for status in PersonalData.CivilStatus])

    @list_route(methods=['get'])
    def employment_statuses(self, request):
        return Response([{"id": sid, "name": name}
                         for sid, name in constants.EMPLOYMENT_STATUSES])

    @list_route(methods=['get'])
    def external_asset_types(self, request):
        return Response([{"id": choice[0], "name": choice[1]}
                         for choice in models.ExternalAsset.Type.choices()])

    @list_route(methods=['get'])
    def constants(self, request):
        return Response({
            'session_length': settings.SESSION_LENGTH,
        })

    @list_route(methods=['get'], url_path='investor-risk-categories')
    def investor_risk_categories(self, request):
        categories = client_models.RiskCategory.objects.all()
        serializer = serializers.InvestorRiskCategorySerializer(categories, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='retirement-saving-categories')
    def retirement_saving_categories(self, request):
        serializer = serializers.EnumSerializer(retirement_models.RetirementPlan.SavingCategory)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='retirement-expense-categories')
    def retirement_expense_categories(self, request):
        serializer = serializers.EnumSerializer(retirement_models.RetirementPlan.ExpenseCategory)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='retirement-housing-categories')
    def retirement_housing_categories(self, request):
        serializer = serializers.EnumSerializer(retirement_models.RetirementPlan.HomeStyle)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='retirement-lifestyle-categories')
    def retirement_lifestyle_categories(self, request):
        serializer = serializers.EnumSerializer(retirement_models.RetirementPlan.LifestyleCategory)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='retirement-lifestyles')
    def retirement_lifestyles(self, request):
        lifestyles = retirement_models.RetirementLifestyle.objects.all().order_by('cost')
        serializer = serializers.RetirementLifestyleSerializer(lifestyles, many=True)
        return Response(serializer.data)
