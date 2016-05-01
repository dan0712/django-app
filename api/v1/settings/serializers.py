from rest_framework import serializers

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import (
    AssetClass, Ticker, GoalType,
    RiskProfileGroup, RiskProfileQuestion, RiskProfileAnswer)

__all__ = (
    'GoalTypeListSerializer',
    'AssetClassListSerializer',
    'TickerListSerializer',
)


class GoalTypeListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = GoalType


class AssetClassListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = AssetClass


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