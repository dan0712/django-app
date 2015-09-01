__author__ = 'cristian'
from ..utils.login import create_login
from main.models import Advisor, User, EmailInvitation, Firm, INVITATION_ADVISOR, INVITATION_SUPERVISOR, \
    INVITATION_TYPE_DICT
from django import forms
from django.views.generic import CreateView, View, TemplateView
from django.utils import safestring
from django.contrib import messages
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from ..base import LegalView
from ...forms import EmailInviteForm

__all__ = ['FirmSummary', 'FirmSupport', 'FirmAdvisorInvites', 'FirmSupervisorInvites', 'FirmSupportForms']


class FirmSummary(TemplateView, LegalView):
    template_name = "firm/summary.html"


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
            firm = request.user.legal_representative.firm
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
            firm = request.user.legal_representative.firm
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

