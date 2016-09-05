from __future__ import unicode_literals

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from main.models import MarketIndex
from .serializers import BenchmarkSerializer


class AvailableListView(ListAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = BenchmarkSerializer

    def get_queryset(self):
        return MarketIndex.objects.all()
