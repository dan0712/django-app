from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import AssetClass, Ticker, GoalType, ActivityLog
from client.models import RiskProfileGroup, RiskProfileQuestion, \
    RiskProfileAnswer


class GoalTypeListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = GoalType
        exclude = ('risk_sensitivity', 'order', 'risk_factor_weights')


class AssetClassListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = AssetClass


class ActivityLogSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = ActivityLog
        exclude = ('format_args',)


class TickerListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = Ticker
        exclude = (
            'data_api', 'data_api_param',
        )


class RiskProfileAnswerSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RiskProfileAnswer
        exclude = (
            'question', 'order', 'score'
        )


class RiskProfileQuestionSerializer(ReadOnlyModelSerializer):
    answers = RiskProfileAnswerSerializer(many=True)

    class Meta:
        model = RiskProfileQuestion
        exclude = (
            'group', 'order'
        )


class RiskProfileGroupSerializer(ReadOnlyModelSerializer):
    questions = RiskProfileQuestionSerializer(many=True)

    class Meta:
        model = RiskProfileGroup
