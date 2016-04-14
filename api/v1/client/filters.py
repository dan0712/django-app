import django_filters

from client.models import Client


class ClientFilter(django_filters.FilterSet):
    class Meta:
        model = Client
        fields = []
