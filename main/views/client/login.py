from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView

from client.models import Client, ClientAccount
from main.constants import PERSONAL_DATA_FIELDS, SUCCESS_MESSAGE
from main.fields import MedicareNumberValidator, TaxFileNumberValidator
from main.forms import BetaSmartzGenericUserSignupForm, PERSONAL_DATA_WIDGETS
from main.models import Advisor, Firm, User

client_sign_up_form_header_1 = """<span class="left blue-circle">1</span>
<h3 class="left">Information to establish your account</h3>"""


class Section:
    def __init__(self, section, form):
        self.header = section.get("header", "")
        self.detail = section.get("detail", None)
        self.css_class = section.get("css_class", None)
        self.fields = []
        for field_name in section["fields"]:
            self.fields.append(form[field_name])


class ClientForm(forms.ModelForm):
    user = forms.CharField(required=False)
    date_of_birth = forms.DateField(input_formats=["%d-%m-%Y"])

    class Meta:
        model = Client
        fields = PERSONAL_DATA_FIELDS + ('advisor', "employment_status",
                                         "income", "occupation", "employer",
                                         "betasmartz_agreement",
                                         "advisor_agreement")

        widgets = PERSONAL_DATA_WIDGETS


class ClientSignUpForm(BetaSmartzGenericUserSignupForm):
    profile = None
    user_profile_type = "client"
    date_of_birth = forms.DateField(input_formats=["%d-%m-%Y"])

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ClientSignUpForm, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.profile = getattr(kwargs['instance'], self.user_profile_type, None)
            profile_kwargs['instance'] = self.profile
        self.profile_form = ClientForm(*args, **profile_kwargs)
        self.fields.update(self.profile_form.fields)
        self.initial.update(self.profile_form.initial)

        self.field_sections = [{"fields": ('first_name', 'middle_name', 'last_name', 'email', 'password',
                                           'confirm_password', 'date_of_birth', 'gender', 'phone_num'),
                                "header": "Information to establish your account"},
                               {"fields": ("employment_status", "occupation", "employer", "income"),
                                "header": "Employment and financial background",
                                "detail": "We are required to ask for your employment and financial background, "
                                          "and your answers allow us to give you better advice. "
                                          "The more accurate information we have, the better advice we can give you.",
                                "css_class": "financial_questions"}]

    def clean(self):
        cleaned_data = super(ClientSignUpForm, self).clean()
        if not (cleaned_data["advisor_agreement"] is True):
            self._errors['advisor_agreement'] = mark_safe('<ul class="errorlist">'
                                                          '<li>You must accept the client\'s agreement'
                                                          ' to continue.</li></ul>')

        return cleaned_data

    def save(self, *args, **kw):
        user = super(ClientSignUpForm, self).save(*args, **kw)
        self.profile = self.profile_form.save(commit=False)
        self.profile.user = user
        self.profile.save()
        self.profile.send_confirmation_email()
        return user

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class ClientSignUp(CreateView):
    template_name = "registration/client_form.html"
    form_class = ClientSignUpForm
    success_url = "/firm/login"

    def __init__(self, *args, **kwargs):
        self.firm = None
        self.advisor = None
        super(ClientSignUp, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ClientSignUp, self).get_context_data(**kwargs)
        ctx["advisor"] = self.advisor
        ctx["firm"] = self.firm
        return ctx

    def get_success_url(self):
        messages.info(self.request, SUCCESS_MESSAGE)
        return super(ClientSignUp, self).get_success_url()

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        token = kwargs["token"]

        try:
            firm = Firm.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            advisor = Advisor.objects.get(token=token, firm=firm)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm
        self.advisor = advisor
        return super(ClientSignUp, self).dispatch(request, *args, **kwargs)


class ClientSignUpPrepopulated(UpdateView):
    template_name = "registration/client_form.html"
    form_class = ClientSignUpForm
    success_url = "/firm/login"
    model = User
    account = None

    def __init__(self, *args, **kwargs):
        self.firm = None
        self.advisor = None
        super(ClientSignUpPrepopulated, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super(ClientSignUpPrepopulated, self).get_queryset()
        qs = qs.filter(prepopulated=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(ClientSignUpPrepopulated, self).get_context_data(**kwargs)
        ctx["advisor"] = self.advisor
        ctx["firm"] = self.firm
        return ctx

    def get_success_url(self):
        client_account = self.object.client.primary_accounts.first()
        client_account.confirmed = True
        client_account.save()
        messages.info(self.request, SUCCESS_MESSAGE)
        return super(ClientSignUpPrepopulated, self).get_success_url()

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        token = kwargs["token"]
        account_token = kwargs["account_token"]

        try:
            firm = Firm.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            advisor = Advisor.objects.get(token=token, firm=firm)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            account = ClientAccount.objects.get(token=account_token, confirmed=False, primary_owner__advisor=advisor)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm
        self.advisor = advisor
        return super(ClientSignUpPrepopulated, self).dispatch(request, *args, **kwargs)
