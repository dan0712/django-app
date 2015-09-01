__author__ = 'cristian'

from ..base import AdminView
from ...models import Firm, INVITATION_LEGAL_REPRESENTATIVE, EmailInvitation, PERSONAL_DATA_FIELDS, Section,\
    PERSONAL_DATA_WIDGETS, BetaSmartzGenericUSerSignupForm
from ...forms import EmailInviteForm
from django.contrib import messages
from main.models import Client, Firm, Advisor, User, LegalRepresentative, FirmData
from django.views.generic import CreateView, View
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponseRedirect
from ..base import LegalView
from django.views.generic.edit import ProcessFormView

__all__ = ["InviteLegalView", "LegalRepresentativeSignUp", 'FirmDataView']


class LegalRepresentativeProfileForm(forms.ModelForm):
    medicare_number = forms.CharField(
        max_length=20,
        label=mark_safe('Medicare # <span class="security-icon"></span>'),
        help_text="Bank-Level Security"
    )

    user = forms.CharField(required=False)

    class Meta:
        model = LegalRepresentative
        fields = PERSONAL_DATA_FIELDS + ('letter_of_authority', 'betasmartz_agreement', 'firm', 'user')

        widgets = PERSONAL_DATA_WIDGETS


class LegalRepresentativeUserForm(BetaSmartzGenericUSerSignupForm):
    user_profile_type = "legal_representative"

    class Meta:
        model = User
        fields = ('email', 'first_name',  'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(LegalRepresentativeUserForm, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            if kwargs['instance']:
                self.profile = kwargs['instance'].legal_representative
                profile_kwargs['instance'] = self.profile
        self.profile_form = LegalRepresentativeProfileForm(*args, **profile_kwargs)
        self.fields.update(self.profile_form.fields)
        self.initial.update(self.profile_form.initial)

        self.field_sections = [{"fields": ('first_name', 'middle_name',  'last_name', 'email', 'password',
                                           'confirm_password', 'date_of_birth', 'gender', 'address_line_1',
                                           'address_line_2', 'city', 'state', 'post_code', 'phone_number'),
                                "header": "Information to establish your account"},
                               {"fields": ('medicare_number', ),
                                "header": "Identity verification",
                                "detail": "We use your Medicare number to verify your identity and protect "
                                          "against fraud."},
                               {"fields": ('security_question_1', 'security_answer_1', 'security_question_2',
                                           'security_answer_2'),
                                "header": "Security",
                                "detail": "We ask for security questions to protect your account."},
                               {"fields": ('letter_of_authority', ),
                                "header": "Authorization",
                                "detail": "BetaSmartz requires a Letter of Authority (PDF) from the new Dealer Group"
                                          " which authorises you to act on their behalf. This letter must"
                                          " be provided by the Dealer Group on Dealer Group company letterhead."}
                               ]

    def save(self, *args, **kw):
        user = super(LegalRepresentativeUserForm, self).save(*args, **kw)
        self.profile = self.profile_form.save(commit=False)
        self.profile.user = user
        self.profile.save()
        return user

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class LegalRepresentativeSignUp(CreateView):
    template_name = "registration/firm_form.html"
    form_class = LegalRepresentativeUserForm
    success_url = "/firm/login"

    def __init__(self, *args, **kwargs):
        self.firm = None
        super(LegalRepresentativeSignUp, self).__init__(*args, **kwargs)

    def get_success_url(self):
        messages.info(self.request, "Your application have been successfully!!!, Please confirm your email address")
        return super(LegalRepresentativeSignUp, self).get_success_url()

    def dispatch(self, request, *args, **kwargs):
        token = kwargs["token"]

        try:
            firm = Firm.objects.get(token=token)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm
        response = super(LegalRepresentativeSignUp, self).dispatch(request, *args, **kwargs)

        if hasattr(response, 'context_data'):
            response.context_data["firm"] = self.firm
        return response


class InviteLegalView(CreateView, AdminView):
    form_class = EmailInviteForm
    template_name = 'admin/betasmartz/legal_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(InviteLegalView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = Firm.objects.get(pk=kwargs["pk"])
            response.context_data["firm"] = firm
            response.context_data["invitation_type"] = INVITATION_LEGAL_REPRESENTATIVE
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=INVITATION_LEGAL_REPRESENTATIVE,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response


class FirmDataForm(forms.ModelForm):

    class Meta:
        model = FirmData
        fields = "__all__"
        widgets = {'office_address_line_1': forms.TextInput(attrs={"placeholder": "Street address"}),
                   "office_address_line_2": forms.TextInput(attrs={"placeholder": "Unit, Floor (optional)"}),
                   'postal_address_line_1': forms.TextInput(attrs={"placeholder": "Street address"}),
                   "postal_address_line_2": forms.TextInput(attrs={"placeholder": "Unit, Floor (optional)"})}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(FirmDataForm, self).__init__(*args, **kwargs)

        self.field_sections = [{"fields": ('afsl_asic', 'afsl_asic_document'),
                                "header": "Dealer Group Details",
                                "detail": "Please provide the adviser’s AFSL Number/ASIC Authorised "
                                          "Representative Number and attach a copy of AFSL."},
                               {"fields": ('office_address_line_1', 'office_address_line_2',
                                           'office_city', 'office_state', 'office_post_code', 'same_address',
                                           'postal_address_line_1', 'postal_address_line_2',
                                           'postal_city', 'postal_state', 'postal_post_code', 'daytime_phone_number',
                                           'mobile_phone_number', 'fax_number', 'alternate_email_address'),
                                "header": "Dealer contact details"},
                               {"fields": ('fee_bank_account_name', 'fee_bank_account_branch_name',
                                           'fee_bank_account_bsb_number', 'fee_bank_account_number',
                                           'fee_bank_account_holder_name'),
                                "header": "Bank  account for fee payments",
                                "detail": "Fees will be paid into the following account Name of financial institution"},
                                {"fields": ('australian_business_number',),
                                 "header": " Taxation details",
                                 "detail": "Please provide the Australian Business Number (ABN) "
                                           "of the Licensee. Fees cannot be paid if an ABN is not supplied."},
                                {"fields": (),
                                 "header": "Investor transfer",
                                 "detail": "If investors are to be transferred to the new dealer group please"
                                           "complete a Bulk Investor Transfer form or Single Investor Transfer form"
                                           " available from betasmartz.com"},

                               ]

    def clean(self):
        cleaned_data = super(FirmDataForm, self).clean()
        self._validate_unique = False

        if cleaned_data.get('same_address', None):
            cleaned_data["postal_address_line_1"] = cleaned_data["office_address_line_1"]
            cleaned_data["postal_address_line_2"] = cleaned_data["office_address_line_2"]
            cleaned_data["postal_city"] = cleaned_data["office_city"]
            cleaned_data["postal_state"] = cleaned_data["office_state"]
            cleaned_data["postal_post_code"] = cleaned_data["office_post_code"]

        self.cleaned_data  = cleaned_data

    def save(self, *args, **kw):
        try:
            self.instance = FirmData.objects.get(firm=self.cleaned_data.get('firm'))
        except ObjectDoesNotExist:
            pass
        return super(FirmDataForm, self).save(*args, **kw)

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class FirmDataView(CreateView, LegalView):
    form_class = FirmDataForm
    template_name = 'registration/firm_details_form.html'
    success_url = '/firm/support/forms'

    def get_object(self):
        if hasattr(self.firm, 'firm_details'):
            return self.firm.firm_details
        else:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return ProcessFormView.get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return ProcessFormView.post(self, request, *args, **kwargs)


class LegalRepresentativeConfirmEmail(View):

    def get(self, request, *args, **kwargs):

        token = kwargs.get("token")

        try:
            legal_representative = LegalRepresentative.objects.get(confirmation_key=token)
        except ObjectDoesNotExist:
            legal_representative = None

        if legal_representative is None:
            messages.error(request, "Bad confirmation code")
        else:
            if legal_representative.is_confirmed:
                messages.error(request, "legal_representative already confirmed")
            else:
                messages.info(request, "You email have been confirmed, you can login in")
                legal_representative.is_confirmed = True

            legal_representative.confirmation_key = None
            legal_representative.save()

        return HttpResponseRedirect('/firm/login')