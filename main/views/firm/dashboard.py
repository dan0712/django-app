from datetime import date

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db.models import Avg, F, Q, Sum
from django.db.models.functions import Coalesce
from django.utils.safestring import mark_safe
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
    TemplateView, UpdateView)
from functools import reduce
from operator import itemgetter

from client.models import Client
from main.constants import (INVITATION_ADVISOR, INVITATION_SUPERVISOR,
    INVITATION_TYPE_DICT)
from main.forms import BetaSmartzGenericUserSignupForm, EmailInviteForm
from main.models import (Advisor, EmailInvitation, Goal, GoalMetric, GoalType,
    Position, Supervisor, Transaction, User)
from main.views.base import LegalView
from notifications.models import Notification
from support.models import SupportRequest
from .filters import FirmActivityFilterSet, FirmAnalyticsAdvisorsFilterSet, \
    FirmAnalyticsClientsFilterSet, FirmAnalyticsOverviewFilterSet


class FirmSupervisorDelete(DeleteView, LegalView):
    template_name = "firm/supervisors-delete.html"
    success_url = 'firm/supervisors' # reverse_lazy('firm:supervisors-delete')
    model = User

    def get_success_url(self):
        messages.success(self.request, "supervisor delete successfully")
        return super(FirmSupervisorDelete, self).get_success_url()

    pass


class SupervisorProfile(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ('can_write',)


class SupervisorUserForm(BetaSmartzGenericUserSignupForm):
    user_profile_type = "supervisor"
    firm = None
    betasmartz_agreement = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(SupervisorUserForm, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.profile = getattr(kwargs['instance'], self.user_profile_type, None)
            profile_kwargs['instance'] = self.profile
        self.profile_form = SupervisorProfile(*args, **profile_kwargs)
        self.fields.update(self.profile_form.fields)
        self.initial.update(self.profile_form.initial)

    def save(self, *args, **kw):
        user = super(SupervisorUserForm, self).save(*args, **kw)
        self.profile = self.profile_form.save(commit=False)
        self.profile.user = user
        self.profile.firm = self.firm
        self.profile.save()
        return user


class SupervisorUserFormEdit(forms.ModelForm):
    user_profile_type = "supervisor"
    firm = None
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput(), required=False)
    new_password = None

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(SupervisorUserFormEdit, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.profile = getattr(kwargs['instance'], self.user_profile_type, None)
            profile_kwargs['instance'] = self.profile
        self.profile_form = SupervisorProfile(*args, **profile_kwargs)
        self.fields.update(self.profile_form.fields)
        self.initial.update(self.profile_form.initial)

    def clean(self):
        cleaned_data = super(SupervisorUserFormEdit, self).clean()

        password1 = cleaned_data.pop('password')
        password2 = cleaned_data.pop('confirm_password')

        if password1:
            if password1 != password2:
                self._errors['confirm_password'] = mark_safe(
                    '<ul class="errorlist"><li>Passwords don\'t match.</li></ul>')
            else:
                self.new_password = make_password(password1)

        return cleaned_data

    def save(self, *args, **kw):
        user = super(SupervisorUserFormEdit, self).save(*args, **kw)
        if self.new_password is not None:
            user.password = self.new_password
            user.save()
        self.profile = self.profile_form.save()
        return user


class FirmSupervisorsCreate(CreateView, LegalView):
    template_name = "firm/supervisors-edit.html"
    form_class = SupervisorUserForm
    success_url = "/firm/users"

    def get_success_url(self):
        messages.success(self.request, "New supervisor created successfully")
        return super(FirmSupervisorsCreate, self).get_success_url()

    def get_form(self, form_class=None):
        form = super(FirmSupervisorsCreate, self).get_form(form_class)
        form.firm = self.firm
        return form


class FirmSupervisorsEdit(UpdateView, LegalView):
    template_name = "firm/supervisors-edit.html"
    form_class = SupervisorUserFormEdit
    success_url = "/firm/supervisors"
    model = User

    def get_success_url(self):
        messages.success(self.request, "Supervisor edited successfully")
        return super(FirmSupervisorsEdit, self).get_success_url()

    def get_form(self, form_class=None):
        form = super(FirmSupervisorsEdit, self).get_form(form_class)
        form.firm = self.firm
        return form


class FirmSupervisors(TemplateView, LegalView):
    template_name = "firm/supervisors.html"

    def get_context_data(self, **kwargs):
        ctx = super(FirmSupervisors, self).get_context_data(**kwargs)
        ctx.update({
            "supervisors": self.firm.supervisors.all(),
            "firm": self.firm,
        })
        return ctx


# OBSOLETED
#class FirmAgreements(TemplateView, LegalView):
#    template_name = "commons/agreements.html"
#
#    def __init__(self, *args, **kwargs):
#        super(FirmAgreements, self).__init__(*args, **kwargs)
#        self.search = ""
#
#    def get(self, request, *args, **kwargs):
#        self.search = request.GET.get("search", self.search)
#        return super(FirmAgreements, self).get(request, *args, **kwargs)
#
#    @property
#    def clients(self):
#        clients = Client.objects.filter(advisor__firm=self.firm, is_confirmed=True, user__prepopulated=False)
#
#        if self.search:
#            sq = Q(user__first_name__icontains=self.search)
#            clients = clients.filter(sq)
#        return clients.all()
#
#    def get_context_data(self, **kwargs):
#        ctx = super(FirmAgreements, self).get_context_data(**kwargs)
#        ctx.update({
#            "clients": self.clients,
#            "search": self.search,
#            "firm": self.firm,
#        })
#        return ctx


class FirmAnalyticsMixin(object):
    """
    @self.firm: current firm to filter by (maybe good to rename it)
    @self.advisor: current advisor to filter by (maybe good to rename it)
    @self.filter: django_filter object (with filter params)
    """
    AGE_STEP = 5
    AGE_RANGE = range(20, 60, AGE_STEP)
    SECONDS_PER_YEAR = 365.25 * 24 * 3600

    def get_queryset_clients(self):
        if not hasattr(self, '_queryset_clients'):
            qs = Client.objects.all()

            if hasattr(self, 'firm'):
                qs = qs.filter_by_firm(self.firm)

            if hasattr(self, 'advisor'):
                qs = qs.filter_by_advisor(self.advisor)

            if hasattr(self, 'client'):
                qs = qs.filter(id=self.client.pk)

            if hasattr(self, 'filter'):
                data = self.filter.data

                risk = data.get('risk')
                if risk:
                    qs = qs.filter_by_risk_level(int(risk))

            self._queryset_clients = qs

        return self._queryset_clients

    def get_queryset_goals(self):
        if not hasattr(self, '_queryset_goals'):
            qs = Goal.objects.all() \
            #.filter(selected_settings__target__gt=0) # ignore "unset" goals

            if hasattr(self, 'firm'):
                qs = qs.filter_by_firm(self.firm)

            if hasattr(self, 'advisor'):
                qs = qs.filter_by_advisor(self.advisor)

            if hasattr(self, 'client'):
                qs = qs.filter_by_client(self.client)

            if hasattr(self, 'filter'):
                data = self.filter.data

                risk = data.get('risk')
                if risk:
                    qs = qs.filter_by_risk_level(int(risk))

            self._queryset_goals = qs

        return self._queryset_goals

    def get_queryset_goals_filterless(self):
        if not hasattr(self, '_queryset_goals_filterless'):
            qs = Goal.objects.all() \
            #.filter(selected_settings__target__gt=0) # ignore "unset" goals

            if hasattr(self, 'firm'):
                qs = qs.filter_by_firm(self.firm)

            if hasattr(self, 'filter'):
                data = self.filter.data
                pass

            self._queryset_goals_filterless = qs

        return self._queryset_goals_filterless

    def get_queryset_positions(self):
        if not hasattr(self, '_queryset_positions'):
            qs = Position.objects.all()

            if hasattr(self, 'firm'):
                qs = qs.filter_by_firm(self.firm)

            if hasattr(self, 'advisor'):
                qs = qs.filter_by_advisor(self.advisor)

            if hasattr(self, 'client'):
                qs = qs.filter_by_client(self.client)

            if hasattr(self, 'filter'):
                data = self.filter.data

                risk = data.get('risk')
                if risk:
                    qs = qs.filter_by_risk_level(int(risk))

            self._queryset_positions = qs

        return self._queryset_positions

    def get_context_worth(self):
        """
        Les:
        Net worth is sum of Goal.total_balance per client
        where they are the primary account holder, age is age of primary account holder.

        Cash flow is a monthly net Transactions in and out of the goals
        for each primary account holder. Ignore incoming dividend type transactions,
        and outgoing fee type transactions. monthly net transactions:
        monthly average for the last year if available, otherwise, whatever's available.
        age: should be “round” to 1 year

        Savva:
        transactions: monthly net transactions for the last month
        """
        qs_goals = self.get_queryset_goals()

        data = []

        for age in self.AGE_RANGE:
            value_worth = qs_goals \
                .filter_by_client_age(age, age + self.AGE_STEP) \
                .values('account__primary_owner__id') \
                .annotate(positions_sum=Coalesce(Sum(
                    F('positions__share') * F('positions__ticker__unit_price')
                ), 0)) \
                .aggregate(
                    positions=Coalesce(Avg('positions_sum'), 0),
                    cash=Coalesce(Avg('cash_balance'), 0),
                )

            value_cashflow = qs_goals \
                .filter_by_client_age(age, age + self.AGE_STEP) \
                .exclude(transactions_to__reason=Transaction.REASON_DIVIDEND) \
                .exclude(transactions_from__reason=Transaction.REASON_FEE) \
                .exclude(transactions_to__status=Transaction.STATUS_PENDING) \
                .exclude(transactions_from__status=Transaction.STATUS_PENDING) \
                .filter(transactions_to__executed__gt=date.today() - relativedelta(months=1)) \
                .filter(transactions_from__executed__gt=date.today() - relativedelta(months=1)) \
                .values('account__primary_owner__id') \
                .annotate(
                    transactions_to_sum=Coalesce(Sum('transactions_to__amount'), 0),
                    transactions_from_sum=Coalesce(Sum('transactions_from__amount'), 0),
                ) \
                .aggregate(
                    transactions_to=Coalesce(Avg('transactions_to_sum'), 0), # should it Sum instead?
                    transactions_from=Coalesce(Avg('transactions_from_sum'), 0), # should it Sum instead?
                )

            data.append({
                'value_worth': value_worth['positions'] + value_worth['cash'],
                'value_cashflow': value_cashflow['transactions_to'] + value_cashflow['transactions_from'],
                'age': age + self.AGE_STEP / 2,
            });

        return data

    def get_context_events(self):
        """
        Les:
        x axis is average age at goal creation and is based on goal.created.
        y axis is sum of Transaction model items where 
        Transaction.status==TRANSACTION_STATUS_EXECUTED
        and  Transaction.to_goal is the goal and Transaction.created 
        is within one week after the Goal.created
        """
        qs_goals = self.get_queryset_goals()
        qs_clients = self.get_queryset_clients()

        data = []
        goal_types = GoalType.objects.all()

        for goal_type in goal_types:
            value = qs_goals \
                .filter(type=goal_type) \
                .aggregate(
                    value=Avg('selected_settings__target')
                )['value']

            # NB be aware. Postgres specific code (to aggregate by date field)
            # (eliminate default ordering - see the model)
            # date_goal = qs_goals \
            #     .filter(type=goal_type) \
            #     .extra(select={
            #         'date': 'avg(extract(epoch FROM {0}.created))' # 'age': 'to_timestamp(avg(extract(epoch FROM {0}.date_of_birth)))'
            #             .format(Goal._meta.db_table) # .format(Client._meta.db_table)
            #     }) \
            #     .order_by() \
            #     .values('date')[0]['date'] or 0
            date_goal = 0

            # NB be aware. Postgres specific code (to aggregate by date field)
            # date_client = qs_clients \
            #     .filter(primary_accounts__all_goals__type=goal_type) \
            #     .extra(select={
            #         'date': 'avg(extract(epoch FROM {0}.date_of_birth))' # 'age': 'to_timestamp(avg(extract(epoch FROM {0}.date_of_birth)))'
            #             .format(Client._meta.db_table)
            #     }) \
            #     .values('date')[0]['date'] or 0
            date_client = 0

            if value and date_client and date_goal:
                # drop categories with no balance (clients)
                data.append({
                    'category': goal_type.name, # maybe we should pass id also
                    'value': value,
                    'age': abs(date_goal - date_client) / self.SECONDS_PER_YEAR,
                });

        return data

    def get_context_positions(self):
        qs_positions = self.get_queryset_positions()

        positions_by_asset_class = qs_positions \
            .annotate(
                asset_class=F('ticker__asset_class'),
                name=F('ticker__asset_class__display_name'),
                color=F('ticker__asset_class__primary_color'),
            ) \
            .values('asset_class', 'name', 'color') \
            .annotate_value()

        positions_by_region = qs_positions \
            .annotate(
                region=F('ticker__region'),
                name=F('ticker__region__name')
            ) \
            .values('region', 'name') \
            .annotate_value()

        positions_by_investment_type = qs_positions \
            .annotate(
                name=F('ticker__asset_class__investment_type'),
            ) \
            .values('name') \
            .annotate_value()

        data = {
            'asset_class': positions_by_asset_class,
            'region': positions_by_region,
            'investment_type': positions_by_investment_type,
        }

        return data


class FirmAnalyticsOverviewView(FirmAnalyticsMixin, TemplateView, LegalView):
    template_name = "firm/analytics.html"

    def get_context_data(self, **kwargs):
        user = SupportRequest.target_user(self.request)
        self.firm  = user.authorised_representative.firm
        self.filter = FirmAnalyticsOverviewFilterSet(self.request.GET)
        return {
            'filter': self.filter,
            'risks': self.get_context_risks(),
            'worth': self.get_context_worth(),
            'events': self.get_context_events(),
            'positions': self.get_context_positions(),
        }

    def get_context_risks(self):
        """
        Les:
        Risk stat cards get their values from the GoalMetric model.
        The risk score is the GoalMetric.configured_val when 
        GoalMetric.metric_type == GoalMetric.METRIC_TYPE_RISK_SCORE.

        Get the metrics for a goal from
        Goal.selected_settings__metric_group__metrics

        There will only be one metric of type METRIC_TYPE_RISK_SCORE in each group.
        """
        qs_goals = self.get_queryset_goals_filterless()

        data = []
        for risk_level_tuple in GoalMetric.RISK_LEVELS:

            value = qs_goals \
                .filter_by_risk_level(risk_level_tuple[0]) \
                .values('account__primary_owner__id') \
                .annotate(positions_sum=Coalesce(Sum(
                    F('positions__share') * F('positions__ticker__unit_price')
                ), 0)) \
                .aggregate(
                    positions=Coalesce(Sum('positions_sum'), 0),
                    cash=Coalesce(Sum('cash_balance'), 0),
                )

            data.append({
                'level': risk_level_tuple[0],
                'name': risk_level_tuple[1],
                'value': value['positions'] + value['cash'],
            })

        # calculate percentages manually, brrr
        data_value_sum = reduce(lambda sum, item: sum + item['value'], data, 0)
        for item in data:
            item['value_percent'] = (item['value'] / data_value_sum
                if data_value_sum else 0)

        return data


class FirmAnalyticsOverviewMetricView(FirmAnalyticsMixin, TemplateView, LegalView):
    template_name = "firm/partials/modal-analytics-metric-content.html"

    def get_context_data(self, **kwargs):
        user = SupportRequest.target_user(self.request)
        self.firm  = user.authorised_representative.firm
        self.filter = FirmAnalyticsOverviewFilterSet(self.request.GET)

        return {
            'risk': self.get_context_risk(),
            'clients': self.get_context_clients(),
            #'positions': self.get_context_positions(),
        }

    def get_context_risk(self):
        param = int(self.filter.data.get('risk', 0))
        risk = dict(GoalMetric.RISK_LEVELS)[param]
        return risk

    def get_context_clients(self):
        qs = self.get_queryset_clients()

        data = qs \
            .order_by('user__last_name') \

        # TODO: add custom annotaion to fetch Goal type names (!!!)
        # the current solution is very temporal and really slow

        return data


class FirmAnalyticsAdvisorsView(ListView, LegalView):
    template_name = "firm/analytics-advisors.html"
    model = Advisor

    # TODO: do we weed that filter at all?
    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        f = FirmAnalyticsAdvisorsFilterSet(self.request.GET, queryset=qs)

        return {
            'filter': f,
        }


class FirmAnalyticsAdvisorsDetailView(FirmAnalyticsMixin, DetailView, LegalView):
    template_name = "firm/partials/modal-analytics-advisor-content.html"
    model = Advisor

    def get_context_data(self, **kwargs):
        context = super(FirmAnalyticsAdvisorsDetailView, self).get_context_data(**kwargs)

        self.advisor = self.object

        context.update(
            worth=self.get_context_worth(),
            events=self.get_context_events(),
            positions=self.get_context_positions(),
        )

        return context


class FirmAnalyticsClientsView(ListView, LegalView):
    template_name = "firm/analytics-clients.html"
    model = Client

    # TODO: do we weed that filter at all?
    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        f = FirmAnalyticsClientsFilterSet(self.request.GET, queryset=qs)

        return {
            'filter': f,
        }


class FirmAnalyticsClientsDetailView(FirmAnalyticsMixin, DetailView, LegalView):
    template_name = "firm/partials/modal-analytics-client-content.html"
    model = Client

    def get_context_data(self, **kwargs):
        context = super(FirmAnalyticsClientsDetailView, self).get_context_data(**kwargs)

        self.client = self.object

        context.update(
            worth=self.get_context_worth(),
            events=self.get_context_events(),
            positions=self.get_context_positions(),
        )

        return context


class FirmActivityView(ListView, LegalView):
    template_name = "firm/activity.html"
    model = Notification

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
        f = FirmActivityFilterSet(self.request.GET, queryset=qs)

        return {
            'filter': f,
        }


class FirmApplicationView(TemplateView, LegalView):
    template_name = "firm/application.html"


class FirmSupportPricingView(TemplateView, LegalView):
    template_name = "firm/support-pricing.html"


class FirmAdvisorClientDetails(DetailView, LegalView):
    template_name = "firm/client-details.html"
    model = Advisor

    def get_queryset(self):
        return super(FirmAdvisorClientDetails, self).get_queryset().filter(firm=self.firm)

    def get_context_data(self, **kwargs):
        ctx = super(FirmAdvisorClientDetails, self).get_context_data(**kwargs)
        client_id = self.kwargs.get("client_id", None)
        client = Client.objects.get(pk=client_id, advisor__firm=self.firm)
        ctx.update({"client": client})
        return ctx


class FirmAdvisorClients(DetailView, LegalView):
    template_name = "firm/advisor-clients.html"
    model = Advisor

    def get_queryset(self):
        return super(FirmAdvisorClients, self).get_queryset().filter(firm=self.firm)

    def get_context_data(self, **kwargs):
        ctx = super(FirmAdvisorClients, self).get_context_data(**kwargs)
        ctx["clients"] = set(map(lambda x: x.primary_owner, self.object.client_accounts))

        return ctx


class FirmAdvisorAccountOverview(DetailView, LegalView):
    template_name = "firm/overview-advisor.html"
    model = Advisor

    def get_queryset(self):
        return super(FirmAdvisorAccountOverview, self).get_queryset().filter(firm=self.firm)

    def get_context_data(self, **kwargs):
        ctx = super(FirmAdvisorAccountOverview, self).get_context_data(
            **kwargs)
        return ctx


class FirmOverview(TemplateView, LegalView):
    template_name = 'firm/overview.html'
    col_dict = {
        "name": 2,
        "cs_number": 0,
        'total_balance': 3,
        'total_return': 4,
        'total_fees': 5,
        'last_action': 6
    }

    def __init__(self, *args, **kwargs):
        super(FirmOverview, self).__init__(*args, **kwargs)
        self.filter = "0"
        self.search = ""
        self.sort_col = "name"
        self.sort_dir = "desc"

    def get(self, request, *args, **kwargs):
        self.filter = request.GET.get("filter", self.filter)
        self.search = request.GET.get("search", self.search)
        self.sort_col = request.GET.get("sort_col", self.sort_col)
        self.sort_dir = request.GET.get("sort_dir", self.sort_dir)
        response = super(FirmOverview, self).get(request, *args, **kwargs)
        return response

    @property
    def advisors(self):
        pre_advisors = self.firm.advisors

        if self.search:
            sq = Q(user__first_name__icontains=self.search)
            pre_advisors = pre_advisors.filter(sq)

        advisors = []
        for advisor in set(pre_advisors.distinct().all()):
            advisors.append(
                [advisor.pk, advisor, advisor.user.full_name, advisor.total_balance,
                 advisor.total_return, advisor.total_fees, advisor.last_action, advisor.user.date_joined])

        reverse = self.sort_dir != "asc"

        advisors = sorted(advisors,
                          key=itemgetter(self.col_dict[self.sort_col]),
                          reverse=reverse)
        return advisors

    def get_context_data(self, **kwargs):
        ctx = super(FirmOverview, self).get_context_data(**kwargs)
        ctx.update({
            "filter": self.filter,
            "search": self.search,
            "sort_col": self.sort_col,
            "sort_dir": self.sort_dir,
            "sort_inverse": 'asc' if self.sort_dir == 'desc' else 'desc',
            "advisors": self.advisors
        })
        return ctx


class FirmSupport(TemplateView, LegalView):
    template_name = "firm/support.html"


class FirmSupportForms(TemplateView, LegalView):
    template_name = "firm/support-forms.html"


class FirmSupervisorInvites(CreateView, LegalView):
    form_class = EmailInviteForm
    template_name = 'firm/supervisor_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(FirmSupervisorInvites, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = request.user.authorised_representative.firm
            invitation_type = INVITATION_SUPERVISOR
            response.context_data["inviter"] = firm
            response.context_data["invite_url"] = firm.supervisor_invite_url
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["invitation_type"] = invitation_type
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response


class FirmAdvisorInvites(CreateView, LegalView):
    form_class = EmailInviteForm
    template_name = 'firm/advisor_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(FirmAdvisorInvites, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = request.user.authorised_representative.firm
            invitation_type = INVITATION_ADVISOR
            response.context_data["inviter"] = firm
            response.context_data["invite_url"] = firm.supervisor_invite_url
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["invitation_type"] = invitation_type
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response
