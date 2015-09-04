__author__ = 'cristian'
from ..utils.login import create_login
from main.models import Advisor, User, EmailInvitation, AccountGroup, ClientAccount
from django import forms
from django.views.generic import CreateView, View, TemplateView, ListView, UpdateView, DetailView
from django.utils import safestring
from django.contrib import messages
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.db.models import Q
from operator import itemgetter
from django.http import Http404
from ..base import AdvisorView
from ...forms import EmailInviteForm
from ...models import INVITATION_CLIENT, INVITATION_TYPE_DICT, Client
from django.utils.safestring import mark_safe

__all__ = ['AdvisorClientInvites', 'AdvisorSummary', 'AdvisorClients', 'AdvisorAgreements', 'AdvisorSupport',
           'AdvisorClientDetails', 'AdvisorCompositeNew', 'AdvisorAccountGroupDetails',
           'AdvisorCompositeEdit', 'AdvisorRemoveAccountFromGroupView', 'AdvisorAccountGroupClients',
           'AdvisorAccountGroupSecondaryDetailView', 'AdvisorAccountGroupSecondaryNewView',
           'AdvisorAccountGroupSecondaryDeleteView', 'AdvisorCompositeSummary']


class AdvisorClientInvitesForm(forms.ModelForm):

    class Meta:
        model = EmailInvitation
        fields = ('email', )

    def clean(self):
        cleaned_data = super(AdvisorClientInvitesForm, self).clean()
        self._validate_unique = False
        return cleaned_data

    def save(self, *args, **kw):
        try:
            invitation = EmailInvitation.objects.get(client_email=self.cleaned_data.get('client_email'),
                                                  advisor=self.cleaned_data.get('advisor'))
        except ObjectDoesNotExist:
            invitation = super(AdvisorClientInvitesForm, self).save(*args, **kw)

        invitation.send()
        return invitation


class AdvisorClientInvites(CreateView, AdvisorView):
    form_class = EmailInviteForm
    template_name = 'advisor/client-invites.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(AdvisorClientInvites, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            advisor = request.user.advisor
            response.context_data["firm"] = advisor.firm
            response.context_data["inviter"] = advisor
            invitation_type = INVITATION_CLIENT
            response.context_data["invitation_type"] = invitation_type
            response.context_data["invite_url"] = advisor.get_invite_url(invitation_type)
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
                                                                              inviter_id=advisor.pk,
                                                                              inviter_type=advisor.content_type,
                                                                              )
        return response


class AdvisorSummary(TemplateView, AdvisorView):
    template_name = "advisor/summary.html"


class AdvisorClientDetails(TemplateView, AdvisorView):
    template_name = "advisor/client-details.html"
    client = None

    def get(self, request, *args, **kwargs):
        client_id = kwargs["pk"]
        client = Client.objects.filter(pk=client_id)
        client = client.filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor])).all()

        if not client:
            raise Http404("Client not found")

        self.client = client[0]

        return super(AdvisorClientDetails, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClientDetails, self).get_context_data(**kwargs)
        ctx.update({"client": self.client})
        return ctx


class AdvisorClients(TemplateView, AdvisorView):
    model = Client
    template_name = 'advisor/clients.html'
    col_dict = {"full_name": 1, "current_balance": 2, 'email_address': 3}

    def __init__(self, *args, **kwargs):
        super(AdvisorClients, self).__init__(*args, **kwargs)
        self.filter = "1"
        self.search = ""
        self.sort_col = "full_name"
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
        pre_clients = self.model.objects

        if self.filter == "1":
            pre_clients = pre_clients.filter(advisor=self.advisor)
        elif self.filter == "2":
            pre_clients = pre_clients.filter(secondary_advisors__in=[self.advisor])
        else:
            pre_clients = pre_clients.filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor]))

        if self.search:
            sq = Q(user__first_name__icontains=self.search) | Q(user__last_name__icontains=self.search)
            pre_clients = pre_clients.filter(sq)

        clients = []

        for client in pre_clients.all():
            relationship = "Primary" if client.advisor == self.advisor else "Secondary"
            clients.append([client.pk, client.full_name, client.total_balance, client.email, relationship])

        reverse = self.sort_dir != "asc"

        clients = sorted(clients, key=itemgetter(self.col_dict[self.sort_col]), reverse=reverse)
        return clients

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClients, self).get_context_data(**kwargs)
        ctx.update({"filter": self.filter,
                    "search": self.search,
                    "sort_col": self.sort_col,
                    "sort_dir": self.sort_dir,
                    "sort_inverse": 'asc' if self.sort_dir == 'desc' else 'desc',
                    "clients": self.clients})
        return ctx


class AdvisorAgreements(TemplateView, AdvisorView):
    template_name = "advisor/agreements.html"


class AdvisorSupport(TemplateView, AdvisorView):
    template_name = "advisor/support.html"


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
                ctx["selected_client"] = Client.objects.get(advisor=self.advisor, pk=ctx["client_id"])
            except ObjectDoesNotExist:
                pass

            ctx["accounts"] = ctx["selected_client"].accounts

        if self.object:
            ctx["object"] = self.object
            if "accounts" in ctx:
                ctx["accounts"] = ctx["accounts"]\
                    .exclude(pk__in=list(map(lambda obj: obj.pk, self.object.accounts.all())))
        ctx["name"] = self.request.GET.get("name", "")
        return ctx

    def form_valid(self, form):
        response = super(AdvisorCompositeForm, self).form_valid(form)
        for account in self.account_list:
            account.add_to_account_group(self.object)
        return response

    def get_success_url(self):
        if self.object:
            return '/composites/{0}/edit'.format(self.object.pk)
        else:
            return '/composites/new'

    def get_queryset(self):
        return super(AdvisorCompositeForm, self).get_queryset().filter(advisor=self.advisor)


class AdvisorCompositeNew(AdvisorCompositeForm, CreateView, AdvisorView):
    template_name = "advisor/composite-form.html"
    model = AccountGroup
    fields = ('advisor', 'name')
    account_list = None

    def post(self, request, *args, **kwargs):
        account_list = request.POST.getlist('accounts')
        account_list = ClientAccount.objects.filter(pk__in=account_list, primary_owner__advisor=self.advisor)
        if account_list.count() == 0:
            messages.error(request, 'Failed to create household. Make sure you add at least one account')
            return HttpResponseRedirect('/composites/new')
        self.account_list = account_list
        return super(AdvisorCompositeNew, self).post(request, *args, **kwargs)

    def get_success_url(self):
        messages.info(self.request, mark_safe('<span class="mpicon accept"></span>Successfully created household'))
        return super(AdvisorCompositeNew, self).get_success_url()


class AdvisorCompositeEdit(AdvisorCompositeForm, UpdateView, AdvisorView):
    template_name = "advisor/composite-form.html"
    model = AccountGroup
    fields = ('advisor', 'name')
    account_list = None

    def post(self, request, *args, **kwargs):
        account_list = request.POST.getlist('accounts')
        account_list = ClientAccount.objects.filter(pk__in=account_list, primary_owner__advisor=self.advisor)
        self.account_list = account_list
        return super(AdvisorCompositeEdit, self).post(request, *args, **kwargs)


class AdvisorRemoveAccountFromGroupView(AdvisorView):

    def post(self, request, *args, **kwargs):

        account_id = kwargs["account_id"]
        account_group_id = kwargs["account_group_id"]

        try:
            account = ClientAccount.objects.get(pk=account_id,
                                                account_group__pk=account_group_id,
                                                primary_owner__advisor=self.advisor)
        except ObjectDoesNotExist:
            raise Http404()

        group_name = account.remove_from_group()

        if group_name:
            return HttpResponseRedirect('/composites/new?name={0}'.format(group_name))
        else:
            return HttpResponseRedirect('/composites/{0}/edit'.format(account_group_id))


class AdvisorAccountGroupDetails(DetailView, AdvisorView):
    template_name = "advisor/account-group-details.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupDetails, self).get_queryset().filter(advisor=self.advisor)

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupDetails, self).get_context_data(**kwargs)
        ctx["object"] = self.object
        return ctx


class AdvisorAccountGroupClients(DetailView, AdvisorView):
    template_name = "advisor/account-group-clients.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupClients, self).get_queryset().filter(advisor=self.advisor)

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupClients, self).get_context_data(**kwargs)
        ctx["object"] = self.object

        ctx["household_clients"] = set(map(lambda x: x.primary_owner, self.object.accounts.all()))

        return ctx


class AdvisorAccountGroupSecondaryDetailView(DetailView, AdvisorView):

    template_name = "advisor/account_group_sharing_form.html"
    model = AccountGroup

    def get_queryset(self):
        return super(AdvisorAccountGroupSecondaryDetailView, self).get_queryset().filter(advisor=self.advisor)


class AdvisorAccountGroupSecondaryNewView(UpdateView, AdvisorView):
    template_name = "advisor/account_group_sharing_form.html"
    model = AccountGroup
    fields = ('secondary_advisors', )
    secondary_advisor = None

    def get_queryset(self):
        return super(AdvisorAccountGroupSecondaryNewView, self).get_queryset().filter(advisor=self.advisor)

    def get_success_url(self):
        msg = '<span class="mpicon accept"></span>'
        msg += 'Successfully added {0} as a secondary advisor to {1}'
        msg = msg.format(self.secondary_advisor.user.get_full_name().title(), self.object.name)
        messages.info(self.request, mark_safe(msg))
        return '/composites/{0}/composite_secondary_advisors/new'.format(self.object.pk)

    def get_form(self, form_class=None):
        form = super(AdvisorAccountGroupSecondaryNewView, self).get_form(form_class)

        def save_m2m():
            secondary_advisors = self.request.POST.get("secondary_advisors", None)
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
            # rebuild secondary advisor for all the clients of this account
            clients = set(map(lambda x: x.primary_owner, self.object.accounts.all()))
            for client in clients:
                client.rebuild_secondary_advisors()

            return self.object

        form.save = save
        form.save_m2m = save_m2m

        return form

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorAccountGroupSecondaryNewView, self).get_context_data(**kwargs)
        ctx["new"] = True
        ctx["s_advisors"] = self.advisor.firm.advisors.exclude(pk=self.advisor.pk)
        ctx["s_advisors"] = ctx["s_advisors"].exclude(
            pk__in=list(map(lambda x: x.pk, self.object.secondary_advisors.all())))

        return ctx


class AdvisorAccountGroupSecondaryDeleteView(AdvisorView):

    def post(self, request, *args, **kwargs):
        account_group_pk = kwargs["pk"]
        s_advisor_pk = kwargs["sa_pk"]

        try:
            account_group = AccountGroup.objects.get(pk=account_group_pk, advisor=self.advisor)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            advisor = Advisor.objects.get(pk=s_advisor_pk)
        except ObjectDoesNotExist:
            raise Http404()

        account_group.secondary_advisors.remove(advisor)

        # rebuild secondary advisor for all the clients of this account
        clients = set(map(lambda x: x.primary_owner, account_group.accounts.all()))
        for client in clients:
            client.rebuild_secondary_advisors()

        messages.info(request, mark_safe('<span class="mpicon accept"></span>Successfully removed secondary '
                                         'advisor from {0}'.format(account_group.name)))

        return HttpResponseRedirect('/composites/{0}/composite_secondary_advisors/new'.format(account_group_pk))


class AdvisorCompositeSummary(TemplateView, AdvisorView):
    model = AccountGroup
    template_name = 'advisor/composite-summary.html'
    col_dict = {"name": 2, "goal_status": 5, 'current_balance': 6, 'return_percentage': 7, 'allocation': 9}

    def __init__(self, *args, **kwargs):
        super(AdvisorCompositeSummary, self).__init__(*args, **kwargs)
        self.filter = "1"
        self.search = ""
        self.sort_col = "name"
        self.sort_dir = "desc"

    def get(self, request, *args, **kwargs):

        self.filter = request.GET.get("filter", self.filter)
        self.search = request.GET.get("search", self.search)
        self.sort_col = request.GET.get("sort_col", self.sort_col)
        self.sort_dir = request.GET.get("sort_dir", self.sort_dir)
        response = super(AdvisorCompositeSummary, self).get(request, *args, **kwargs)
        return response

    @property
    def groups(self):

        pre_groups = self.model.objects

        if self.filter == "1":
            pre_groups = pre_groups.filter(advisor=self.advisor)
        elif self.filter == "2":
            pre_groups = pre_groups.filter(secondary_advisors__in=[self.advisor])
        else:
            pre_groups = pre_groups.filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor]))

        if self.search:
            sq = Q(name__icontains=self.search)
            pre_groups = pre_groups.filter(sq)

        groups = []
        for group in pre_groups.all():
            relationship = "Primary" if group.advisor == self.advisor else "Secondary"
            first_account = group.accounts.first()
            groups.append([group.pk, group, group.name, first_account.account_type_name, relationship,
                          group.on_track, group.total_balance, group.total_returns, group.since, group.allocation,
                          group.stocks_percentage, group.bonds_percentage])

        reverse = self.sort_dir != "asc"

        groups = sorted(groups, key=itemgetter(self.col_dict[self.sort_col]), reverse=reverse)
        return groups

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorCompositeSummary, self).get_context_data(**kwargs)
        ctx.update({"filter": self.filter,
                    "search": self.search,
                    "sort_col": self.sort_col,
                    "sort_dir": self.sort_dir,
                    "sort_inverse": 'asc' if self.sort_dir == 'desc' else 'desc',
                    "groups": self.groups})
        return ctx