__author__ = 'cristian'

from main.models import Advisor, User
from django import forms
from django.views.generic import CreateView, View
from django.utils import safestring
from django.contrib import messages
import uuid
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

__all__ = ["AdvisorSignUpView", "AdvisorConfirmEmail"]


class AdvisorConfirmEmail(View):

    def get(self, request, *args, **kwargs):

        token = kwargs.get("token")

        try:
            advisor = Advisor.objects.get(confirmation_key=token)
        except ObjectDoesNotExist:
            advisor = None

        if advisor is None:
            messages.error(request, "Bad confirmation code")
        else:
            if advisor.is_accepted:
                if advisor.is_confirmed:
                    messages.error(request, "Advisor already confirmed")
                else:
                    advisor.is_confirmed = True
                    advisor.confirmation_key = None
                    advisor.save()

                    messages.info(request, "You email have been confirmed, you can login in")
            else:
                messages.error(request, "Wait till ours team approve your application")

        return HttpResponseRedirect('/firm/login')


class AdvisorForm(forms.ModelForm):

    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = Advisor
        fields = ('date_of_birth', 'phone_number', 'firm')


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
            if kwargs['instance']:
                self.advisor = kwargs['instance'].advisor
                advisor_kwargs['instance'] = self.advisor
        self.advisor_form = AdvisorForm(*args, **advisor_kwargs)
        self.fields.update(self.advisor_form.fields)
        self.initial.update(self.advisor_form.initial)

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        self._validate_unique = False
        self.errors.update(self.advisor_form.errors)
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')

        if password1 and (password1 != password2):
            self._errors['confirm_password'] = safestring.mark_safe(u'<ul class="errorlist"><li>Passwords don\'t '
                                                                    u'match.</li></ul>')
        # check if user already exist
        try:
            user = User.objects.get(email=cleaned_data.get('email'))
        except ObjectDoesNotExist:
            user = None

        if user is not None:
            if hasattr(user, 'advisor'):
                self._errors['email'] = safestring.mark_safe(u'<ul class="errorlist"><li>User already has an'
                                                             u' advisor account</li></ul>')
            else:
                # confirm password
                if not user.check_password(password1):
                    self._errors['email'] = safestring.mark_safe(u'<ul class="errorlist"><li>User already '
                                                                 u'exists</li></ul>')
        cleaned_data["password"] = make_password(self.cleaned_data["password"])
        return cleaned_data

    def save(self, *args, **kw):
        # check if user already exist
        try:
            user = User.objects.get(email=self.cleaned_data.get('email'))
        except ObjectDoesNotExist:
            user = None

        if user is None:
            super(UserForm, self).save(*args, **kw)

        else:
            user.first_name = self.cleaned_data.get('first_name')
            user.last_name = self.cleaned_data.get('last_name')
            user.middle_name = self.cleaned_data.get('middle_name')
            user.save()
            self.instance = user

        new_advisor = Advisor(user=self.instance,
                              work_phone=self.cleaned_data.get('work_phone'),
                              confirmation_key=str(uuid.uuid4()),
                              token=str(uuid.uuid4()),
                              firm=self.cleaned_data.get('firm'),
                              date_of_birth=self.cleaned_data.get('date_of_birth'))
        new_advisor.save()
        return self.instance


class AdvisorSignUpView(CreateView):
    form_class = UserForm
    template_name = "advisor-sign-up.html"
    success_url = "/firm/login"

    def get_success_url(self):
        messages.info(self.request, "Your application have been successfully!!!, you will receive a confirmation email"
                                    " within the next hours after our team approve it")

        return super(AdvisorSignUpView, self).get_success_url()