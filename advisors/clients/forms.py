from __future__ import unicode_literals

from django import forms


class EmailInvitationForm(forms.ModelForm):
    class Meta:
        fields = 'first_name', 'middle_name', 'last_name', 'email'
