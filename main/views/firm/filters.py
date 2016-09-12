from dateutil.relativedelta import relativedelta
import logging
from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
import django_filters as filters
from django.utils.timezone import now

from notifications.models import Notification

from main.models import Advisor, Goal, GoalMetric
from client.models import Client

ATTRS_ONCHANGE= {'onchange': 'this.form.submit();'}

logger = logging.getLogger('main.views.firm.filters')


class SearchFilter(filters.CharFilter):
    """
    Experimental
    """
    def __init__(self, lookup_fields=[], *args, **kwargs):
        self.lookup_fields = lookup_fields
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, queryset, value):
        q = Q()
        for lookup_field in self.lookup_fields:
            params = {lookup_field + '__icontains': value}
            q = Q(**params) | q
            params = {lookup_field + '__icontains': value.capitalize()}
            q |= Q(**params)
            # check for capitalized versions too

        return queryset.filter(q)


class PeriodFilter(filters.ChoiceFilter):
    PERIOD_CHOICES = (
        (None, '- Time period -'),
        (None, 'All time'),
        ('30', '1mo'),
        ('365', '1yr'),
    )

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get('choices', self.PERIOD_CHOICES)
        super(PeriodFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        dt = now().today()
        dt = dt - relativedelta(days=int(value))

        qs = qs.filter(timestamp__gte=dt)
        return qs


class UserGroupFilter(filters.ChoiceFilter):
    _GROUPS_DEFAULT = ('Advisors', 'Clients') # 'Supervisors'

    def __init__(self, groups=None, *args, **kwargs):
        # @group: list of groups (by name)
        # this query in initialization is causing an error trying to
        # call the sqlite3 database when loading main tests
        self.GROUPS = kwargs.get('groups', self._GROUPS_DEFAULT)
        try:
            groups = list(
                Group.objects
                .filter(name__in=self.GROUPS)
                .values_list('id', 'name')
            )
        except:
            logger.error('Did not find expected groups for UserGroupFilter')
        choices = [
                (None, '- Users -'),
                (None, 'All'),
            ]
        if groups:
            choices += groups

        kwargs['choices'] = choices
        super(UserGroupFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        qs = qs.filter(users__groups__id=value)

        return qs


class WorthFilter(filters.ChoiceFilter):
    WORTH_CHOICES = (
        (None, '- Worth -'),
        (None, 'Any'),
    ) + Client.WORTH_CHOICES

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get('choices', self.WORTH_CHOICES)
        super(WorthFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        return qs


class RiskFilter(filters.MultipleChoiceFilter):
    def __init__(self, *args, **kwargs):
        choices = [
                (None, 'Any'),
            ] + list(GoalMetric.RISK_LEVELS)

        kwargs['choices'] = kwargs.get('choices', choices)
        super(RiskFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        return qs


class FirmActivityFilterSet(filters.FilterSet):
    VERB_CHOICES = (
        (None, '- Activity -'),
        (None, 'All'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )

    group = UserGroupFilter(widget=forms.Select(attrs=ATTRS_ONCHANGE),
        groups=('Advisors', 'Clients', 'Supervisors'))
    timestamp = PeriodFilter(widget=forms.Select(attrs=ATTRS_ONCHANGE))
    verb = filters.ChoiceFilter(choices=VERB_CHOICES, widget=forms.Select(attrs=ATTRS_ONCHANGE))

    class Meta:
        model = Notification
        fields = ['group', 'verb', 'timestamp']


class FirmAnalyticsOverviewFilterSet(filters.FilterSet):
    risk = RiskFilter(widget=forms.CheckboxSelectMultiple(attrs=ATTRS_ONCHANGE))
    worth = WorthFilter(widget=forms.Select(attrs=ATTRS_ONCHANGE))
    #group = UserGroupFilter(widget=forms.Select(attrs=ATTRS_ONCHANGE))

    class Meta:
        model = Goal # not in use
        fields = ['risk', 'worth'] # 'group',  'risk',


class FirmAnalyticsAdvisorsFilterSet(filters.FilterSet):
    search = SearchFilter(widget=forms.TextInput(
        attrs=dict({'placeholder': 'Search...'}, **ATTRS_ONCHANGE)),
        lookup_fields=['user__first_name', 'user__last_name', 'user__email'])

    class Meta:
        model = Advisor
        fields = ['search']


class FirmAnalyticsClientsFilterSet(filters.FilterSet):
    search = SearchFilter(widget=forms.TextInput(
        attrs=dict({'placeholder': 'Search...'}, **ATTRS_ONCHANGE)),
        lookup_fields=['user__first_name', 'user__last_name', 'user__email'])

    class Meta:
        model = Client
        fields = ['search']


class FirmAnalyticsGoalsAdvisorsFilterSet(filters.FilterSet):
    advisor = SearchFilter(widget=forms.TextInput(
        attrs=dict({'placeholder': 'Advisor'}, **ATTRS_ONCHANGE)),
        lookup_fields=['user__first_name', 'user__last_name', 'user__email'])

    class Meta:
        model = Advisor
        fields = ['advisor']


class FirmAnalyticsGoalsClientsFilterSet(filters.FilterSet):
    client = SearchFilter(widget=forms.TextInput(
        attrs=dict({'placeholder': 'Client'}, **ATTRS_ONCHANGE)),
        lookup_fields=['user__first_name', 'user__last_name', 'user__email'])

    class Meta:
        model = Client
        fields = ['client']
