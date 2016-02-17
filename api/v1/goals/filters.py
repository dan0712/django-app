import django_filters

from main.models import Goal


class GoalFilter(django_filters.FilterSet):
    class Meta:
        model = Goal
        fields = []
