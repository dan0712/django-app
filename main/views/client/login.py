from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView

from main.models import (
    Client, Firm, Advisor, User,
    BetaSmartzGenericUSerSignupForm,
    ClientAccount, TaxFileNumberValidator, MedicareNumberValidator,
    PERSONAL_DATA_WIDGETS, PERSONAL_DATA_FIELDS, SUCCESS_MESSAGE,
)

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
    medicare_number = forms.CharField(
        label=mark_safe('Medicare # <span class="security-icon"></span>'),
        help_text="Bank-Level Security"
    )
    date_of_birth = forms.DateField(input_formats=["%d-%m-%Y"])

    class Meta:
        model = Client
        fields = PERSONAL_DATA_FIELDS + ('advisor', 'tax_file_number', "provide_tfn", "associated_to_broker_dealer",
                                         "ten_percent_insider", 'public_position_insider', 'us_citizen',
                                         "employment_status", "net_worth", "income", "occupation", "employer",
                                         "betasmartz_agreement", "advisor_agreement")

        widgets = {"ten_percent_insider": forms.RadioSelect(),
                   "associated_to_broker_dealer": forms.RadioSelect(),
                   'public_position_insider': forms.RadioSelect(),
                   'us_citizen': forms.RadioSelect(),
                   "provide_tfn": forms.RadioSelect(),
                   }

        widgets.update(PERSONAL_DATA_WIDGETS)


class ClientSignUpForm(BetaSmartzGenericUSerSignupForm):
    profile = None
    user_profile_type = "client"
    tax_file_number = forms.CharField(required=False)
    medicare_number = forms.CharField()
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
                                           'confirm_password', 'date_of_birth', 'gender', 'address_line_1',
                                           'address_line_2', 'city', 'state', 'phone_number'),
                                "header": "Information to establish your account"},
                               {"fields": ('medicare_number',),
                                "header": "Identity verification",
                                "detail": "We use your Medicare number to verify your identity and protect "
                                          "against fraud."},
                               {"fields": ('provide_tfn', 'tax_file_number',),
                                "header": "Tax File Number (TFN)",
                                "detail": "You are not required to provide your TFN, however if you don't we will"
                                          " have to deduct tax at the highest marginal tax rate (BetaSmartz "
                                          "recommends you provide your TFN, claim exemption or advise us of"
                                          " your non-resident status."},
                               {"fields": ('security_question_1', 'security_answer_1', 'security_question_2',
                                           'security_answer_2'),
                                "header": "Security",
                                "detail": "We ask for security questions to protect your account."},
                               {"fields": ("employment_status", "occupation", "employer", "net_worth", "income"),
                                "header": "Employment and financial background",
                                "detail": "We are required to ask for your employment and financial background, "
                                          "and your answers allow us to give you better advice. "
                                          "The more accurate information we have, the better advice we can give you.",
                                "css_class": "financial_questions"},
                               {"fields": ("associated_to_broker_dealer", "ten_percent_insider",
                                           'public_position_insider', 'us_citizen'),
                                "header": "Regulatory questions",
                                "detail": "We are required by law to ask about the following rare situations."
                                          " Most users will answer No:",
                                "css_class": "r_questions"}]

    def clean(self):
        cleaned_data = super(ClientSignUpForm, self).clean()
        if not (cleaned_data["advisor_agreement"] is True):
            self._errors['advisor_agreement'] = mark_safe('<ul class="errorlist">'
                                                          '<li>You must accept the client\'s agreement'
                                                          ' to continue.</li></ul>')

        medicare_number = cleaned_data.get("medicare_number", "").replace(" ", "").replace("/", "")
        tax_file_number = cleaned_data.get("tax_file_number", "")
        provide_tfn = cleaned_data.get("provide_tfn", 0)

        if provide_tfn == 0:
            if not tax_file_number:
                self._errors['tax_file_number'] = mark_safe('<ul class="errorlist">'
                                                            '<li>Tax file number is required.</li></ul>')
            else:
                valid, msg = TaxFileNumberValidator()(tax_file_number)
                if not valid:
                    self._errors['tax_file_number'] = mark_safe('<ul class="errorlist">'
                                                                '<li>{0}</li></ul>'.format(msg))
        else:
            cleaned_data["tax_file_number"] = ""

        valid, msg = MedicareNumberValidator()(medicare_number)
        if not valid:
            self._errors['medicare_number'] = mark_safe('<ul class="errorlist">'
                                                        '<li>{0}</li></ul>'.format(msg))

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
