from __future__ import unicode_literals

from rest_framework import serializers

from main.models import MarketIndex


class BenchmarkSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()

    class Meta:
        model = MarketIndex
        fields = ('id', 'display_name', 'description', 'url',
                  'currency', 'region')
