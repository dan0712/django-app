__author__ = 'cristian'

from ..utils.login import create_login
from main.models import Advisor, User
from django import forms
from django.views.generic import FormView
from django.utils import safestring
from django.contrib import messages




__all__ = ["advisor_login", "AdvisorSignUpView"]

advisor_login = create_login(Advisor, 'advisor')


class AdvisorForm(forms.ModelForm):

    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}))

    class Meta:
        model = Advisor
        fields = ('date_of_birth', 'work_phone', 'firm' )


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'first_name',  'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        advisor_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.advisor = kwargs['instance'].advisor
            advisor_kwargs['instance'] = self.advisor
        self.advisor_form = AdvisorForm(*args, **advisor_kwargs)
        self.fields.update(self.advisor_form.fields)
        self.initial.update(self.advisor_form.initial)

        # define fields order if needed
        self.fields.keyOrder = (
            'email',
            'first_name',
            'middle_name',
            'last_name',
            'date_of_birth',
            'work_phone',
            'firm',
            # etc
            'password',
        )

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        self.errors.update(self.advisor_form.errors)
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')

        if password1 and (password1 != password2):
            self._errors['confirm_password'] = safestring.mark_safe(u'<ul class="errorlist"><li>Passwords don\'t '
                                                                    u'match.</li></ul>')
        return cleaned_data


class AdvisorSignUpView(FormView):
    form_class = UserForm
    template_name = "advisor-sign-up.html"
    success_url = "/advisor/login"

    def get_success_url(self):
        messages.info(self.request, "Your application have been successfully!!!, you will receive a confirmation email"
                                    " within the next hours after our team approve it")
        return super(AdvisorSignUpView, self).get_success_url()