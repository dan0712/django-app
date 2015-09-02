__author__ = 'cristian'
from ..utils.login import create_login
from main.models import Advisor, User, EmailInvitation
from django import forms
from django.views.generic import CreateView, View, TemplateView
from django.utils import safestring
from django.contrib import messages
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from ..base import AdvisorView
from ...forms import EmailInviteForm
from ...models import INVITATION_CLIENT, INVITATION_TYPE_DICT

__all__ = ['AdvisorClientInvites', 'AdvisorSummary', 'AdvisorClients', 'AdvisorAgreements', 'AdvisorSupport']


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


class AdvisorClients(TemplateView, AdvisorView):
    template_name = "advisor/clients.html"


class AdvisorAgreements(TemplateView, AdvisorView):
    template_name = "advisor/agreements.html"


class AdvisorSupport(TemplateView, AdvisorView):
    template_name = "advisor/support.html"
