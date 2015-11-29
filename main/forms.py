__author__ = 'cristian'

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from main.models import EmailInvitation


class EmailInviteForm(forms.ModelForm):
    class Meta:
        model = EmailInvitation
        fields = ('email', 'invitation_type', 'inviter_type', 'inviter_id')

    def clean(self):
        cleaned_data = super(EmailInviteForm, self).clean()
        self._validate_unique = False
        return cleaned_data

    def save(self, *args, **kw):
        try:
            invitation = EmailInvitation.objects.get(email=self.cleaned_data.get('email'),
                                                     inviter_type=self.cleaned_data.get('inviter_type'),
                                                     inviter_id=self.cleaned_data.get('inviter_id'),
                                                     invitation_type=self.cleaned_data.get('invitation_type'))
        except ObjectDoesNotExist:
            invitation = super(EmailInviteForm, self).save(*args, **kw)

        invitation.send()
        return invitation
