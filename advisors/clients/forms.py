from __future__ import unicode_literals

from django import forms

from client.models import EmailInvite


class EmailInviteForm(forms.ModelForm):
    class Meta:
        model = EmailInvite
        fields = 'first_name', 'middle_name', 'last_name', 'email', 'reason'
