__author__ = 'cristian'

from ..utils.login import create_login
from main.models import Client, Firm, Advisor, User
from django.views.generic import CreateView
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.safestring import mark_safe

__all__ = ["client_login", 'ClientSignUp']

client_login = create_login(Client, 'client', '')

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
    medicare_number = forms.CharField(
        max_length=20,
        label=mark_safe('Medicare # <span class="security-icon"></span>'),
        help_text="Bank-Level Security"
    )

    class Meta:
        model = Client
        fields = ('advisor', 'date_of_birth', 'gender', 'address_line_1', 'address_line_2', 'city', 'state',
                  'post_code', 'phone_number', 'medicare_number', 'tax_file_number', "provide_tfn",
                  'security_question_1', "security_question_2", "security_answer_1", "security_answer_2",
                  "associated_to_broker_dealer", "ten_percent_insider")
        widgets = {"ten_percent_insider": forms.RadioSelect(),
                   "associated_to_broker_dealer": forms.RadioSelect(),
                   "gender": forms.RadioSelect(),
                   "provide_tfn": forms.RadioSelect(),
                   "date_of_birth": forms.TextInput(attrs={"placeholder": "MM-DD-YYYY"}),
                   'address_line_1': forms.TextInput(attrs={"placeholder": "Street address"}),
                   "address_line_2": forms.TextInput(attrs={"placeholder": "Apartment, Suite, Unit, Floor (optional)"})}


class ClientSignUpForm(forms.ModelForm):

    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'first_name',  'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ClientSignUpForm, self).__init__(*args, **kwargs)
        client_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            if kwargs['instance']:
                self.client = kwargs['instance'].client
                client_kwargs['instance'] = self.client
        self.client_form = ClientForm(*args, **client_kwargs)
        self.fields.update(self.client_form.fields)
        self.initial.update(self.client_form.initial)

        self.field_sections = [{"fields": ('first_name', 'middle_name',  'last_name', 'email', 'password',
                                           'confirm_password', 'date_of_birth', 'gender', 'address_line_1',
                                           'address_line_2', 'city', 'state', 'post_code', 'phone_number'),
                                "header": "Information to establish your account"},
                               {"fields": ('medicare_number', ),
                                "header": "Identity verification",
                                "detail": "We use your Medicare number to verify your identity and protect "
                                          "against fraud."},
                               {"fields": ('provide_tfn', 'tax_file_number', ),
                                "header": "Tax File Number (TFN)",
                                "detail": "You are not required to provide your TFN, however if you don't we will"
                                          " have to deduct tax at the highest marginal tax rate (BetaSmartz "
                                          "recommends you provide your TFN, claim exemption or advise us of"
                                          " your non-resident status."},
                               {"fields": ('security_question_1', 'security_answer_1', 'security_question_2',
                                           'security_answer_2'),
                                "header": "Security",
                                "detail": "We ask for security questions to protect your account."},
                               {"fields": ("associated_to_broker_dealer", "ten_percent_insider"),
                                "header": "Regulatory questions",
                                "detail": "We are required by law to ask about the following rare situations."
                                          " Most users will answer No:",
                               "css_class": "r_questions"}]

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class ClientSignUp(CreateView):
    template_name = "registration/client_form.html"
    form_class = ClientSignUpForm

    def __init__(self, *args, **kwargs):
        self.firm = None
        self.advisor = None
        super(ClientSignUp, self).__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = super(ClientSignUp, self).get(request, *args, **kwargs)
        response.context_data["advisor"] = self.advisor
        response.context_data["firm"] = self.firm
        return response

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        token = kwargs["token"]

        try:
            firm = Firm.objects.get(firm_slug=slug)
        except ObjectDoesNotExist:
            raise Http404()

        try:
            advisor = Advisor.objects.get(token=token, firm=firm)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm
        self.advisor = advisor
        return super(ClientSignUp, self).dispatch(request, *args, **kwargs)