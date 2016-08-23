from datetime import datetime

from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views.generic import (CreateView, DetailView, TemplateView, UpdateView)
from operator import itemgetter

from address.models import Address, Region
from client.models import Client, ClientAccount
from main.constants import (ACCOUNT_TYPES, INVITATION_CLIENT,
                            INVITATION_TYPE_DICT)
from main.forms import EmailInviteForm
from main.models import (AccountGroup, Advisor, EmailInvitation,
                         Platform, User)
from main.views.base import AdvisorView, ClientView
from support.models import SupportRequest


class AdvisorClientInvites(CreateView, AdvisorView):
    form_class = EmailInviteForm
    template_name = 'advisor/clients-invites.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def get(self, request, *args, **kwargs):
        invite_type = request.GET.get('invite_type', None)
        if invite_type is not None and invite_type in ("prepopulated",
                                                       "blank"):
            self.template_name = 'advisor/clients-invites-create-account-type.html'
        response = super(CreateView, self).get(request, *args, **kwargs)
        response.context_data["invite_type_new_client"] = invite_type
        return response

    def dispatch(self, request, *args, **kwargs):
        response = super(AdvisorClientInvites, self).dispatch(request, *args,
                                                              **kwargs)
        if hasattr(response, 'context_data'):
            advisor = request.user.advisor
            response.context_data["firm"] = advisor.firm
            response.context_data["inviter"] = advisor
            invitation_type = INVITATION_CLIENT
            response.context_data["invitation_type"] = invitation_type
            response.context_data["invite_url"] = advisor.get_invite_url(
                invitation_type, None)
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(
                invitation_type)].title()
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(
                invitation_type=invitation_type,
                inviter_id=advisor.pk,
                inviter_type=advisor.content_type, )
        return response


class AdvisorOverview(TemplateView, AdvisorView):
    template_name = "advisor/overview.html"


class AdvisorClientDetails(TemplateView, AdvisorView):
    template_name = "advisor/clients-detail.html"
    client = None

    def get(self, request, *args, **kwargs):
        client_id = kwargs["pk"]
        client = Client.objects.filter(pk=client_id)
        client = client.filter(Q(advisor=self.advisor) | Q(
            secondary_advisors__in=[self.advisor])).all()

        if not client:
            raise Http404("Client not found")

        self.client = client[0]

        return super(AdvisorClientDetails, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClientDetails, self).get_context_data(**kwargs)
        ctx.update({"client": self.client})
        return ctx


class AdvisorClientInviteNewView(TemplateView, AdvisorView):
    """Docstring for AdvisorClientInviteNewView. """

    template_name = 'advisor/clients-invites-create.html'


class AdvisorClients(TemplateView, AdvisorView):
    model = Client
    template_name = 'advisor/clients.html'
    col_dict = {"full_name": 1, "current_balance": 2, 'email_address': 3}

    def __init__(self, *args, **kwargs):
        super(AdvisorClients, self).__init__(*args, **kwargs)
        self.filter = "0"
        self.search = ""
        self.sort_col = "current_balance"
        self.sort_dir = "desc"

    def get(self, request, *args, **kwargs):

        self.filter = request.GET.get("filter", self.filter)
        self.search = request.GET.get("search", self.search)
        self.sort_col = request.GET.get("sort_col", self.sort_col)
        self.sort_dir = request.GET.get("sort_dir", self.sort_dir)
        response = super(AdvisorClients, self).get(request, *args, **kwargs)
        return response

    @property
    def clients(self):
        pre_clients = self.model.objects.filter(user__prepopulated=False)

        if self.filter == "1":
            pre_clients = pre_clients.filter(advisor=self.advisor)
        elif self.filter == "2":
            pre_clients = pre_clients.filter(
                secondary_advisors__in=[self.advisor])
        else:
            pre_clients = pre_clients.filter(Q(advisor=self.advisor) | Q(
                secondary_advisors__in=[self.advisor]))

        if self.search:
            sq = Q(user__first_name__icontains=self.search) | Q(
                user__last_name__icontains=self.search)
            pre_clients = pre_clients.filter(sq)

        clients = []

        for client in set(pre_clients.distinct().all()):
            relationship = "Primary" if client.advisor == self.advisor else "Secondary"
            clients.append([client.pk, client.full_name, client.total_balance,
                            client.email, relationship])

        reverse = self.sort_dir != "asc"

        clients = sorted(clients,
                         key=itemgetter(self.col_dict[self.sort_col]),
                         reverse=reverse)
        return clients

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClients, self).get_context_data(**kwargs)
        ctx.update({
            "filter": self.filter,
            "search": self.search,
            "sort_col": self.sort_col,
            "sort_dir": self.sort_dir,
            "sort_inverse": 'asc' if self.sort_dir == 'desc' else 'desc',
            "clients": self.clients
        })
        return ctx


class AdvisorAgreements(TemplateView, AdvisorView):
    template_name = "commons/agreements.html"

    def __init__(self, *args, **kwargs):
        super(AdvisorAgreements, self).__init__(*args, **kwargs)
        self.search = ""

    def get(self, request, *args, **kwargs):
        self.search = request.GET.get("search", self.search)
        return super(AdvisorAgreements, self).get(request, *args, **kwargs)

    @property
    def clients(self):
        clients = self.advisor.clients
        if self.search:
            sq = Q(user__first_name__icontains=self.search)
            clients = clients.filter(sq)
        return clients.all()

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAgreements, self).get_context_data(**kwargs)
        ctx.update({
            "clients": self.clients,
            "search": self.search,
            "firm": self.advisor.firm,
        })
        return ctx


class AdvisorSupport(TemplateView, AdvisorView):
    template_name = "advisor/support.html"


class AdvisorForms(TemplateView, AdvisorView):
    template_name = "advisor/support-forms.html"


class AdvisorCompositeForm:
    def get_context_data(self, **kwargs):
        ctx = super(AdvisorCompositeForm, self).get_context_data(**kwargs)
        client_id = self.request.GET.get('client_id', None)

        if client_id:

            try:
                ctx["client_id"] = int(client_id)
            except ValueError:
                return ctx

            try:
                ctx["selected_client"] = Client.objects.get(
                    advisor=self.advisor,
                    pk=ctx["client_id"])
            except ObjectDoesNotExist:
                pass

            ctx["accounts"] = ctx["selected_client"].accounts

        if self.object:
            ctx["object"] = self.object
            if "accounts" in ctx:
                ctx["accounts"] = ctx["accounts"] \
                    .exclude(pk__in=list(map(lambda obj: obj.pk, self.object.accounts.all())))
        ctx["name"] = self.request.GET.get("name", "")
        return ctx

    def form_valid(self, form):
        response = super(AdvisorCompositeForm, self).form_valid(form)

        if self.account_list:
            for account in self.account_list:
                account.add_to_account_group(self.object)

        return response

    def get_success_url(self):
        if self.object:
            return reverse_lazy('advisor:composites-edit', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('advisor:composites-create')

    def get_queryset(self):
        return super(AdvisorCompositeForm, self).get_queryset().filter(
            advisor=self.advisor)


class AdvisorCompositeNew(AdvisorCompositeForm, CreateView, AdvisorView):
    template_name = "advisor/composites-create.html"
    model = AccountGroup
    fields = ('advisor', 'name')
    account_list = None

    """
    def post(self, request, *args, **kwargs):
        account_list = request.POST.getlist('accounts')
        account_list = ClientAccount.objects.filter(
            pk__in=account_list,
            primary_owner__advisor=self.advisor)
        if account_list.count() == 0:
            redirect = reverse_lazy('advisor:composites-create')
            messages.error(request,
                'Failed to create household. Make sure you add at least one account')
            return HttpResponseRedirect(redirect)
        self.account_list = account_list
        return super(AdvisorCompositeNew, self).post(request, *args, **kwargs)
    """

    def get_success_url(self):
        messages.info(self.request, mark_safe(
            '<span class="mpicon accept"></span>Successfully created household'))

        return super(AdvisorCompositeNew, self).get_success_url()


class AdvisorCompositeEdit(AdvisorCompositeForm, UpdateView, AdvisorView):
    template_name = "advisor/composites-edit.html"
    model = AccountGroup
    fields = ('advisor', 'name')
    account_list = None

    def post(self, request, *args, **kwargs):
        account_list = request.POST.getlist('accounts')
        account_list = ClientAccount.objects.filter(
            pk__in=account_list,
            primary_owner__advisor=self.advisor)
        self.account_list = account_list
        return super(AdvisorCompositeEdit, self).post(request, *args, **kwargs)


class AdvisorRemoveAccountFromGroupView(AdvisorView):
    def post(self, request, *args, **kwargs):

        account_id = kwargs["account_id"]
        account_group_id = kwargs["account_group_id"]

        try:
            account = ClientAccount.objects.get(
                pk=account_id,
                account_group__pk=account_group_id,
                primary_owner__advisor=self.advisor)
        except ObjectDoesNotExist:
            raise Http404()

        group_name = account.remove_from_group()

        if group_name:
            # account group deleted (cause no accounts in it any more)
            redirect = reverse_lazy('advisor:overview')
        else:
            # account group not deleted (just the account)
            redirect = reverse_lazy('advisor:composites-edit',
                kwargs={'pk': account_group_id})

        return HttpResponseRedirect(redirect)


class AdvisorAccountGroupDetails(DetailView, AdvisorView):
    template_name = "advisor/composites-detail.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupDetails, self).get_queryset() \
            .filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor])).distinct()

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupDetails, self).get_context_data(
            **kwargs)
        ctx["object"] = self.object
        return ctx


class AdvisorAccountGroupClients(DetailView, AdvisorView):
    template_name = "advisor/composites-detail-clients.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupClients, self).get_queryset() \
            .filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor])).distinct()

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupClients, self).get_context_data(
            **kwargs)
        ctx["object"] = self.object

        ctx["household_clients"] = set(map(lambda x: x.primary_owner,
                                           self.object.accounts.all()))

        return ctx


class AdvisorAccountGroupSecondaryDetailView(DetailView, AdvisorView):
    template_name = "advisor/composites-detail-secondary-advisors.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupSecondaryDetailView,
                     self).get_queryset().filter(advisor=self.advisor)


class AdvisorAccountGroupSecondaryCreateView(UpdateView, AdvisorView):
    template_name = "advisor/composites-detail-secondary-advisors.html"
    model = AccountGroup
    fields = ('secondary_advisors',)
    secondary_advisor = None

    def get_queryset(self):
        return super(AdvisorAccountGroupSecondaryCreateView,
                     self).get_queryset().filter(advisor=self.advisor)

    def get_success_url(self):
        msg = '<span class="mpicon accept"></span>'
        msg += 'Successfully added {0} as a secondary advisor to {1}'
        msg = msg.format(self.secondary_advisor.user.get_full_name().title(),
                         self.object.name)

        messages.info(self.request, mark_safe(msg))

        return reverse_lazy('advisor:composites-detail-secondary-advisors-create',
                kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(AdvisorAccountGroupSecondaryCreateView,
                     self).get_form(form_class)

        def save_m2m():
            secondary_advisors = self.request.POST.get("secondary_advisors",
                                                       None)
            if secondary_advisors:

                try:
                    advisor = Advisor.objects.get(pk=secondary_advisors)
                except ObjectDoesNotExist:
                    raise Http404()

                self.object.secondary_advisors.add(advisor)
                self.secondary_advisor = advisor
            else:
                raise Http404()

        def save(*args, **kwargs):
            save_m2m()
            return self.object

        form.save = save
        form.save_m2m = save_m2m

        return form

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupSecondaryCreateView,
                    self).get_context_data(**kwargs)
        ctx["new"] = True
        ctx["s_advisors"] = self.advisor.firm.advisors.exclude(
            pk=self.advisor.pk)
        ctx["s_advisors"] = ctx["s_advisors"].exclude(
            pk__in=list(map(lambda x: x.pk, self.object.secondary_advisors.all(
            ))))

        return ctx


class AdvisorAccountGroupSecondaryDeleteView(AdvisorView):
    def post(self, request, *args, **kwargs):
        account_group_pk = kwargs["pk"]
        s_advisor_pk = kwargs["sa_pk"]

        try:
            account_group = AccountGroup.objects.get(pk=account_group_pk,
                                                     advisor=self.advisor)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            advisor = Advisor.objects.get(pk=s_advisor_pk)
        except ObjectDoesNotExist:
            raise Http404()

        account_group.secondary_advisors.remove(advisor)

        messages.info(request, mark_safe(
            '<span class="mpicon accept"></span>Successfully removed secondary '
            'advisor from {0}'.format(account_group.name)))

        return HttpResponseRedirect(
            reverse_lazy('advisor:composites-detail-secondary-advisors-create',
                kwargs={'pk': account_group_pk})
        )


class AdvisorCompositeOverview(TemplateView, AdvisorView):
    model = AccountGroup
    template_name = 'advisor/overview.html'
    col_dict = {
        "name": 2,
        "goal_status": 5,
        'current_balance': 6,
        'return_percentage': 7,
        'allocation': 9
    }

    def __init__(self, *args, **kwargs):
        super(AdvisorCompositeOverview, self).__init__(*args, **kwargs)
        self.filter = "0"
        self.search = ""
        self.sort_col = "name"
        self.sort_dir = "desc"

    def get(self, request, *args, **kwargs):

        self.filter = request.GET.get("filter", self.filter)
        self.search = request.GET.get("search", self.search)
        self.sort_col = request.GET.get("sort_col", self.sort_col)
        self.sort_dir = request.GET.get("sort_dir", self.sort_dir)
        response = super(AdvisorCompositeOverview, self).get(request, *args,
                                                            **kwargs)
        return response

    @property
    def groups(self):
        pre_groups = self.model.objects

        if self.filter == "1":
            pre_groups = pre_groups.filter(advisor=self.advisor)
        elif self.filter == "2":
            pre_groups = pre_groups.filter(
                secondary_advisors__in=[self.advisor])
        else:
            pre_groups = pre_groups.filter(Q(advisor=self.advisor) | Q(
                secondary_advisors__in=[self.advisor]))

        if self.search:
            sq = Q(name__icontains=self.search)
            pre_groups = pre_groups.filter(sq)

        groups = []
        for group in set(pre_groups.distinct().all()):
            relationship = "Primary" if group.advisor == self.advisor else "Secondary"
            first_account = group.accounts.first()
            if first_account is None:
                continue

            groups.append(
                [group.pk, group, group.name, first_account,
                 relationship, group.on_track, group.total_balance,
                 group.total_returns, group.since, group.allocation,
                 group.stocks_percentage, group.bonds_percentage,
                 group.core_percentage, group.satellite_percentage])

        reverse = self.sort_dir != "asc"

        groups = sorted(groups,
                        key=itemgetter(self.col_dict[self.sort_col]),
                        reverse=reverse)
        return groups

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorCompositeOverview, self).get_context_data(**kwargs)
        ctx.update({
            "filter": self.filter,
            "search": self.search,
            "sort_col": self.sort_col,
            "sort_dir": self.sort_dir,
            "sort_inverse": 'asc' if self.sort_dir == 'desc' else 'desc',
            "groups": self.groups
        })
        return ctx


class AdvisorClientAccountChangeFee(UpdateView, AdvisorView):
    model = ClientAccount
    fields = ('custom_fee',)
    template_name = 'advisor/form-fee.js'
    content_type = 'text/javascript'

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClientAccountChangeFee, self).get_context_data(
            **kwargs)
        ctx["object"] = self.object
        ctx["platform"] = Platform.objects.first()
        ctx["firm"] = self.advisor.firm
        html_output = render_to_string("advisor/form-fee.html",
                                       RequestContext(self.request, ctx))
        html_output = mark_safe(html_output.replace("\n", "\\n").replace(
            '"', '\\"').replace("'", "\\'"))
        ctx["html_output"] = html_output
        return ctx

    def get_queryset(self):
        return super(AdvisorClientAccountChangeFee, self).get_queryset().distinct() \
            .filter(Q(account_group__advisor=self.advisor) | Q(account_group__secondary_advisors__in=[self.advisor]))

    def get_form(self, form_class=None):
        form = super(AdvisorClientAccountChangeFee, self).get_form(form_class)
        old_save = form.save

        def save(*args, **kwargs):
            instance = old_save(*args, **kwargs)
            if self.request.POST.get("is_custom_fee", "false") == "false":
                instance.custom_fee = 0
                instance.save()

            return instance

        form.save = save
        return form

    def get_success_url(self):
        return '/composites/{0}'.format(self.object.account_group.pk)


class AdvisorSupportGettingStarted(AdvisorView, TemplateView):
    template_name = 'advisor/support-getting-started.html'


USER_DETAILS = ('first_name', 'middle_name', 'last_name', 'email')

UNSET_ADDRESS_ID = '__XX_UNSET_XX__'


class PrepopulatedUserForm(forms.ModelForm):
    advisor = None
    account_class = ""

    def define_advisor(self, advisor):
        self.advisor = advisor

    def add_account_class(self, account_class):
        self.account_class = account_class

    class Meta:
        model = User
        fields = USER_DETAILS

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.instance = User(password="KONfLOP212=?hlokifksi21f6s1",
                             prepopulated=True,
                             **self.cleaned_data)
        self.instance.save()
        # create client instance
        defs = {
            'address': 'Default Unset Address',
            'region': Region.objects.get_or_create(country='AU', name='New South Wales')[0]
        }
        # TODO: Change this so we only create a client once all the info is complete from external onboarding.
        # TODO: Until then, they're just a user.
        new_client = Client(
            advisor=self.advisor,
            user=self.instance,
            client_agreement=self.advisor.firm.client_agreement_url,
            residential_address=Address.objects.get_or_create(global_id=UNSET_ADDRESS_ID, defaults=defs)[0]
        )
        new_client.save()
        personal_account = new_client.accounts_all.all()[0]
        personal_account.account_class = self.account_class
        personal_account.save()
        return self.instance


class CreateNewClientPrepopulatedView(AdvisorView, TemplateView):
    template_name = 'advisor/clients-invites-create-profile.html'
    form_class = PrepopulatedUserForm
    account_type = None
    invite_type = None

    def post(self, request, *args, **kwargs):

        try:
            user = User.objects.get(email=request.POST.get("email", None))

            if not user.prepopulated:
                messages.error(request, "User already exists")
                response = super(CreateNewClientPrepopulatedView, self).get(
                    request, *args, **kwargs)
                response.context_data["form"] = self.form_class(
                    data=request.POST)
                return response
            else:
                return HttpResponseRedirect(
                    reverse_lazy('advisor:clients-invites-create-personal-details',
                        kwargs={'pk': user.client.pk})
                )

        except ObjectDoesNotExist:
            pass

        form = self.form_class(data=request.POST)

        if form.is_valid():
            form.define_advisor(self.advisor)
            form.add_account_class(self.account_type)
            user = form.save()
            if self.invite_type == "blank":
                return HttpResponseRedirect(
                    reverse_lazy('advisor:clients-invites-create-confirm',
                        kwargs={'pk': user.client.pk}) + '?invitation_type=blank'
                )

            else:
                return HttpResponseRedirect(self.get_success_url())

        else:
            response = super(CreateNewClientPrepopulatedView, self).get(
                request, *args, **kwargs)
            response.context_data["form"] = form
            return response

    def dispatch(self, request, *args, **kwargs):
        self.account_type = request.GET.get("account_type", request.POST.get(
            "account_type", None))
        self.invite_type = request.GET.get("invite_type", request.POST.get(
            "invite_type", None))

        if self.account_type not in ["joint_account", "trust_account"]:
            messages.error(request, "Please select an account type")

            return HttpResponseRedirect(
                reverse_lazy('advisor:clients-invites') \
                + '?invitation_type={0}'.format(self.invite_type)
            )

        return super(CreateNewClientPrepopulatedView, self).dispatch(
            request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(CreateNewClientPrepopulatedView, self).get(request, *args,
                                                                **kwargs)

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return reverse_lazy('advisor:clients-invites')

    def get_context_data(self, **kwargs):
        context_data = super(CreateNewClientPrepopulatedView,
                             self).get_context_data(**kwargs)
        context_data["account_type"] = self.account_type
        context_data["invite_type_new_email"] = self.invite_type
        context_data['form'] = self.form_class()

        return context_data


PERSONAL_DETAILS = ('date_of_birth', "month", "day", "year", "gender", "phone_num", "residential_address")


class BuildPersonalDetailsForm(forms.ModelForm):
    month = forms.CharField(required=False, max_length=150)
    day = forms.CharField(required=False, max_length=150)
    year = forms.CharField(required=False, max_length=150)

    class Meta:
        model = Client
        fields = PERSONAL_DETAILS

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(BuildPersonalDetailsForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        for k, field in self.fields.items():
            field.required = False
        if self.instance and self.instance.date_of_birth:
            self.fields["month"].initial = self.instance.date_of_birth.month
            self.fields["year"].initial = self.instance.date_of_birth.year
            self.fields["day"].initial = self.instance.date_of_birth.day

    def clean(self):
        cleaned_data = super(BuildPersonalDetailsForm, self).clean()
        year = cleaned_data.get("year", "")
        month = cleaned_data.get("month", "")
        day = cleaned_data.get("day", "")

        if "" not in (day, month, year):

            try:
                date_b = "{year}-{month}-{day}".format(year=year,
                                                       month=month,
                                                       day=day)

                date_b = datetime.strptime(date_b, "%Y-%m-%d")
                cleaned_data["date_of_birth"] = date_b
            except ValueError:
                date_b = None
                self._errors['date_of_birth'] = mark_safe(
                    u'<ul class="errorlist"><li>Invalid Date</li></ul>')

            if date_b:
                cleaned_data["date_of_birth"] = date_b
                date_diff = now().year - date_b.year
                if date_diff < 18:
                    self._errors['date_of_birth'] = \
                        mark_safe(u'<ul class="errorlist"><li>Client under 18 </li></ul>')

        return cleaned_data


class BuildPersonalDetails(AdvisorView, UpdateView):
    template_name = 'advisor/clients-invites-create-personal-details.html'
    model = Client
    form_class = BuildPersonalDetailsForm

    def get_queryset(self):
        q = super(BuildPersonalDetails, self).get_queryset()
        q.filter(advisor=self.advisor, user__prepopulated=True)
        return q

    def get_success_url(self):
        return reverse_lazy('advisor:clients-invites-create-financial-details',
                kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context_data = super(BuildPersonalDetails, self).get_context_data(
            **kwargs)
        context_data["years"] = list(range(1895, now().year))
        context_data["days"] = list(range(1, 31))
        context_data["years"].reverse()
        return context_data


FINANCIAL_DETAILS = ('employment_status', 'occupation', 'employer', 'income',
                     'associated_to_broker_dealer',
                     'ten_percent_insider', 'public_position_insider',
                     'us_citizen')


class BuildFinancialDetailsForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = FINANCIAL_DETAILS

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(BuildFinancialDetailsForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        for k, field in self.fields.items():
            field.required = False


class BuildFinancialDetails(AdvisorView, UpdateView):
    template_name = 'advisor/clients-invites-create-financial-details.html'
    model = Client
    form_class = BuildFinancialDetailsForm

    def get_queryset(self):
        q = super(BuildFinancialDetails, self).get_queryset()
        q.filter(advisor=self.advisor, user__prepopulated=True)
        return q

    def get_success_url(self):
        return reverse_lazy('advisor:clients-invites-create-confirm',
                kwargs={'pk': self.object.pk})


class BuildConfirm(AdvisorView, TemplateView):
    template_name = 'advisor/clients-invites-create-confirm.html'
    object = None
    invitation_type = None

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        self.invitation_type = self.request.GET.get(
            "invitation_type", self.request.POST.get('invitation_type', None))

        try:
            self.object = Client.objects.get(pk=pk,
                                             advisor=request.user.advisor)
        except ObjectDoesNotExist:
            raise Http404()

        return super(BuildConfirm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(BuildConfirm, self).get_context_data(**kwargs)
        attributes = []
        user_values = []
        user_verbose_names = []
        for key in USER_DETAILS:
            user_verbose_names.append(User._meta.get_field_by_name(key)[
                                          0].verbose_name.title())
            user_values.append(getattr(self.object.user,
                                       "get_{0}_display".format(key), getattr(
                    self.object.user, key, "")))
        user_dict = dict(zip(user_verbose_names, user_values))
        user_dict["Full Name"] = "{0} {1} {2}".format(
            user_dict.pop("First Name"), user_dict.pop("Middle Name(S)"),
            user_dict.pop("Last Name"))

        verbose_names = []
        values = []
        for key in PERSONAL_DETAILS:
            if key in ("month", "year", "day"):
                continue
            verbose_names.append(Client._meta.get_field_by_name(key)[
                                     0].verbose_name.title())
            values.append(getattr(self.object, "get_{0}_display".format(key),
                                  getattr(self.object.user, key, "")))

        personal_dict = dict(zip(verbose_names, values))

        verbose_names = []
        values = []
        for key in FINANCIAL_DETAILS:
            verbose_names.append(Client._meta.get_field_by_name(key)[
                                     0].verbose_name.title())
            values.append(getattr(self.object, "get_{0}_display".format(key),
                                  getattr(self.object.user, key, "")))

        financial_dict = dict(zip(verbose_names, values))

        for k, v in user_dict.items():
            if v:
                attributes.append({"name": k, "value": v})

        if self.invitation_type != "blank":

            for k, v in personal_dict.items():
                if v:
                    attributes.append({"name": k, "value": v})

            for k, v in financial_dict.items():
                if v:
                    attributes.append({"name": k, "value": v})

        context_data["attributes"] = attributes
        context_data["inviter_type"] = self.advisor.content_type
        context_data["inviter_id"] = self.advisor.pk
        context_data["invitation_type"] = INVITATION_CLIENT
        context_data["email"] = self.object.user.email

        return context_data


class AdvisorCreateNewAccountForExistingClientSelectAccountType(AdvisorView, TemplateView):
    template_name = "advisor/clients-invites-create-account-type.html"
    client = None

    def dispatch(self, request, *args, **kwargs):
        client_pk = kwargs["pk"]
        user = SupportRequest.target_user(request)
        advisor = user.advisor

        try:
            client = advisor.clients.get(pk=client_pk)
        except ObjectDoesNotExist:
            raise PermissionDenied()

        self.client = client

        return super(AdvisorCreateNewAccountForExistingClientSelectAccountType,
                     self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorCreateNewAccountForExistingClientSelectAccountType, self).get_context_data(**kwargs)
        ctx_data["client"] = self.client
        return ctx_data


class AdvisorCreateNewAccountForExistingClient(AdvisorView, CreateView):
    template_name = "advisor/clients-invites-confirm-account.html"
    model = ClientAccount
    fields = ('primary_owner', 'account_class')
    client = None
    account_class = None

    def get_success_url(self):
        messages.success(self.request, "New account confirmation email sent successfully.")
        return reverse_lazy('advisor:clients-detail', kwargs={'pk': self.client.pk})

    def dispatch(self, request, *args, **kwargs):
        client_pk = kwargs["pk"]
        account_class = request.POST.get("account_type", request.GET.get("account_type", None))

        if account_class is None:
            account_class = request.POST.get("account_class", request.GET.get("account_class", None))

        if account_class not in ["joint_account", "trust_account"]:
            raise Http404()

        user = SupportRequest.target_user(request)
        advisor = user.advisor

        try:
            client = advisor.clients.get(pk=client_pk)
        except ObjectDoesNotExist:
            raise PermissionDenied()

        self.client = client
        self.account_class = account_class

        return super(AdvisorCreateNewAccountForExistingClient, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super(AdvisorCreateNewAccountForExistingClient, self).form_valid(form)
        self.object.send_confirmation_email()
        return response

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorCreateNewAccountForExistingClient, self).get_context_data(**kwargs)
        ctx_data["client"] = self.client
        ctx_data["account_class"] = self.account_class
        account_type_name = self.account_class
        for i in ACCOUNT_TYPES:
            if i[0] == self.account_class:
                account_type_name = i[1]
        ctx_data["account_type_name"] = account_type_name
        return ctx_data


class ConfirmClientNewAccountForm(forms.ModelForm):
    class Meta:
        model = ClientAccount
        fields = ("confirmed",)

    def clean_confirmed(self):
        confirmed = self.cleaned_data["confirmed"]
        if not confirmed:
            self._errors["confirmed"] = "Please confirm"
        return confirmed


class ConfirmClientNewAccount(ClientView, UpdateView):
    model = ClientAccount
    form_class = ConfirmClientNewAccountForm
    template_name = "advisor/clients-invites-confirm.html"
    success_url = "/client/app"

    def post(self, request, *args, **kwargs):
        if self.is_advisor:
            raise Http404()
        return super(ConfirmClientNewAccount, self).post(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ConfirmClientNewAccount, self).get_queryset()
        qs = qs.filter(primary_owner=self.client, confirmed=False)
        return qs
