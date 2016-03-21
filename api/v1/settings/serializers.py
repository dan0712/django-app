from rest_framework import serializers

from main.models import (
    AssetClass, Ticker, GoalType,
)

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
        exclude = (
            'asset_class_explanation', 'tickers_explanation',
        )

class TickerListSerializer(serializers.ModelSerializer):
    """
    Experimental
    """
    class Meta:
        model = Ticker
        exclude = (
            'data_api', 'data_api_param',
        )
