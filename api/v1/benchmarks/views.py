from __future__ import unicode_literals

from dateutil import parser
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.constants import EPOCH_DT
from main.models import MarketIndex
from .serializers import BenchmarkSerializer


class AvailableListView(generics.ListAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = BenchmarkSerializer

    def get_queryset(self):
        return MarketIndex.objects.all()


class ReturnsView(generics.ListAPIView):
    permission_classes = IsAuthenticated,

    def get_query_date(self, name):
        try:
            dt = parser.parse(self.request.query_params.get(name))
            return dt.strftime('%Y-%m-%d')
        except (AttributeError, ValueError, OverflowError):
            pass

    def filter_queryset(self, queryset):
        params = {}
        sd = self.get_query_date('sd')
        ed = self.get_query_date('ed')
        if sd:
            params['date__gte'] = sd
        if ed:
            params['date__lte'] = ed
        if params:
            return queryset.filter(**params)
        return queryset

    def get_queryset(self):
        return generics.get_object_or_404(MarketIndex, **{
            self.lookup_field: self.kwargs[self.lookup_field]
        }).daily_prices.all()

    def get_data(self, daily_prices: list):
        prices = []
        last_price = None
        for row in daily_prices:
            try:
                prices.append(((row.date - EPOCH_DT).days,
                               row.price - last_price))
            except TypeError:
                pass
            last_price = row.price
        return prices

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            r = self.get_paginated_response(self.get_data(page))
        else:
            r = Response(self.get_data(queryset))
        return r
