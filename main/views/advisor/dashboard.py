__author__ = 'cristian'
from ..utils.login import create_login
from main.models import Advisor, User, EmailInvitation
from django import forms
from django.views.generic import CreateView, View, TemplateView, ListView
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

__all__ = ['AdvisorClientInvites', 'AdvisorSummary', 'AdvisorClients', 'AdvisorAgreements', 'AdvisorSupport',
           'AdvisorClientDetails']


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
        pre_clients = self.model.objects.filter(Q(advisor=self.advisor) | Q(secondary_advisors__in=[self.advisor]))

        if self.filter == "1":
            pre_clients = pre_clients.filter(advisor=self.advisor)
        elif self.filter == "2":
            pre_clients = pre_clients.filter(secondary_advisors__in=[self.advisor])

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


class AdvisorSupport(CreateView, AdvisorView):
    template_name = "advisor/create-household.html"

