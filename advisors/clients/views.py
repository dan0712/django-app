from __future__ import unicode_literals

import logging

from django import http
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, \
    ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from operator import itemgetter

from advisors.clients.forms import EmailInviteForm
from client.models import Client, ClientAccount, EmailInvite
from main.constants import ACCOUNT_TYPES
from main.views.base import AdvisorView
from support.models import SupportRequest


logger = logging.getLogger(__name__)


class AdvisorClients(TemplateView, AdvisorView):
    model = Client
    template_name = 'advisor/clients/list.html'
    col_dict = {"full_name": 1, 'status': 2, "current_balance": 3, 'email_address': 4}

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
            clients.append([client.pk, client.full_name, client.on_track, client.total_balance,
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


class AdvisorClientDetails(TemplateView, AdvisorView):
    template_name = "advisor/clients/detail.html"
    client = None

    def get(self, request, *args, **kwargs):
        client_id = kwargs["pk"]
        client = Client.objects.filter(pk=client_id)
        client = client.filter(Q(advisor=self.advisor) | Q(
            secondary_advisors__in=[self.advisor])).all()

        if not client:
            raise http.Http404("Client not found")

        self.client = client[0]

        return super(AdvisorClientDetails, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(AdvisorClientDetails, self).get_context_data(**kwargs)
        ctx.update({"client": self.client})
        return ctx


class AdvisorCreateNewAccountForExistingClient(AdvisorView, CreateView):
    template_name = "advisor/clients/invites/confirm-account.html"
    model = ClientAccount
    fields = ('primary_owner', 'account_class')
    client = None
    account_class = None

    def get_success_url(self):
        messages.success(self.request, "New account confirmation email sent successfully.")
        return reverse_lazy('advisor:clients:detail', kwargs={'pk': self.client.pk})

    def dispatch(self, request, *args, **kwargs):
        client_pk = kwargs["pk"]
        account_class = request.POST.get("account_type", request.GET.get("account_type", None))

        if account_class is None:
            account_class = request.POST.get("account_class", request.GET.get("account_class", None))

        if account_class not in ["joint_account", "trust_account"]:
            raise http.Http404()

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


class AdvisorClientInvites(ListView, AdvisorView):
    template_name = 'advisor/clients/invites/list.html'
    context_object_name = 'invites'

    def get_queryset(self):
        return self.advisor.invites.all()


class AdvisorNewClientInviteView(CreateView, AdvisorView):
    template_name = 'advisor/clients/invites/new.html'
    form_class = EmailInviteForm

    def get_success_url(self):
        return reverse('advisor:clients:invites')

    def form_valid(self, form):
        self.object = invite = form.save(commit=False)
        invite.advisor = self.advisor
        invite.save()
        try:
            invite.send()
            messages.success(self.request, 'Invitation email sent.')
        except ValidationError as e:
            messages.error(self.request, str(e))
        except Exception as e:
            logger.error('Cannot send invitation email (%s)', e)
            messages.error(self.request, 'Cannot send invitation email!')
        return http.HttpResponseRedirect(self.get_success_url())


class AdvisorCreateNewAccountForExistingClientSelectAccountType(AdvisorView, TemplateView):
    template_name = "advisor/clients/invites/create-account-type.html"
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


class AdvisorNewClientResendInviteView(SingleObjectMixin, AdvisorView):
    queryset = EmailInvite.objects.all()

    def post(self, request, *args, **kwargs):
        invite = self.get_object()
        invite.send()
        messages.info(self.request, "Invite sent successfully!")
        return http.HttpResponseRedirect(reverse('advisor:clients:invites'))
