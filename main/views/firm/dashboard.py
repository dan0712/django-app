__author__ = 'cristian'
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from main.models import EmailInvitation, INVITATION_ADVISOR, INVITATION_SUPERVISOR, \
    INVITATION_TYPE_DICT
from ..base import LegalView
from ...forms import EmailInviteForm
from main.models import Advisor
from django.db.models import Q
from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth import (
    load_backend, BACKEND_SESSION_KEY, login as auth_login, logout as auth_logout)
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View
from main.models import Advisor, User, EmailInvitation, AccountGroup, ClientAccount, Platform
from operator import itemgetter
from ..base import AdvisorView, ClientView
from ...forms import EmailInviteForm
from ...models import INVITATION_CLIENT, INVITATION_TYPE_DICT, Client, ACCOUNT_CLASSES


__all__ = ['FirmSummary', 'FirmAdvisorAccountSummary', 'FirmAdvisorClients',
           'FirmSupport', 'FirmAdvisorInvites', 'FirmSupervisorInvites', 'FirmAgreements',
           'FirmSupportForms', "FirmAdvisorClientDetails", "FirmSupportGettingStarted"]


class FirmAgreements(TemplateView, LegalView):
    template_name = "commons/agreements.html"

    def __init__(self, *args, **kwargs):
        super(FirmAgreements, self).__init__(*args, **kwargs)
        self.search = ""

    def get(self, request, *args, **kwargs):
        self.search = request.GET.get("search", self.search)
        return super(FirmAgreements, self).get(request, *args, **kwargs)

    @property
    def clients(self):
        clients = Client.objects.filter(advisor__firm=self.firm, is_confirmed=True, user__prepopulated=False)

        if self.search:
            sq = Q(user__first_name__icontains=self.search)
            clients = clients.filter(sq)
        return clients.all()

    def get_context_data(self, **kwargs):
        ctx = super(FirmAgreements, self).get_context_data(**kwargs)
        ctx.update({
            "clients": self.clients,
            "search": self.search,
            "firm": self.firm,
        })
        return ctx


class FirmSupportGettingStarted(TemplateView, LegalView):
    template_name = "firm/support-getting-started.html"


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


class FirmAdvisorAccountSummary(DetailView, LegalView):
    template_name = "firm/advisor-summary.html"
    model = Advisor

    def get_queryset(self):
        return super(FirmAdvisorAccountSummary, self).get_queryset().filter(firm=self.firm)

    def get_context_data(self, **kwargs):
        ctx = super(FirmAdvisorAccountSummary, self).get_context_data(
            **kwargs)
        return ctx


class FirmSummary(TemplateView, LegalView):
    template_name = 'firm/summary.html'
    col_dict = {
        "name": 2,
        "cs_number": 0,
        'total_balance': 3,
        'total_return': 4,
        'total_fees': 5,
        'last_action': 6

    }

    def __init__(self, *args, **kwargs):
        super(FirmSummary, self).__init__(*args, **kwargs)
        self.filter = "0"
        self.search = ""
        self.sort_col = "name"
        self.sort_dir = "desc"

    def get(self, request, *args, **kwargs):

        self.filter = request.GET.get("filter", self.filter)
        self.search = request.GET.get("search", self.search)
        self.sort_col = request.GET.get("sort_col", self.sort_col)
        self.sort_dir = request.GET.get("sort_dir", self.sort_dir)
        response = super(FirmSummary, self).get(request, *args, **kwargs)
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
        ctx = super(FirmSummary, self).get_context_data(**kwargs)
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
