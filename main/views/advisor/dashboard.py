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
    template_name = "advisor/client-invites.html"
    form_class = AdvisorClientInvitesForm
    success_url = "/advisor/client_invites"

    def get(self, request, *args, **kwargs):
        response = super(AdvisorClientInvites, self).get(request, *args, **kwargs)
        response.context_data["client_invites"] = EmailInvitation.objects.filter(advisor=request.user.advisor,
                                                                              is_user=False)
        return response


class AdvisorSummary(TemplateView, AdvisorView):
    template_name = "advisor/summary.html"


class AdvisorClients(TemplateView, AdvisorView):
    template_name = "advisor/clients.html"


class AdvisorAgreements(TemplateView, AdvisorView):
    template_name = "advisor/agreements.html"


class AdvisorSupport(TemplateView, AdvisorView):
    template_name = "advisor/support.html"
