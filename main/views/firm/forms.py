__author__ = 'cristian'

from ..base import AdminView
from ...models import Firm, AUTHORIZED_REPRESENTATIVE, EmailInvitation, PERSONAL_DATA_FIELDS, Section,\
    PERSONAL_DATA_WIDGETS, BetaSmartzGenericUSerSignupForm, INVITATION_ADVISOR, INVITATION_SUPERVISOR,\
    INVITATION_TYPE_DICT, SUCCESS_MESSAGE
from ...forms import EmailInviteForm
from django.contrib import messages
from main.models import Client, Firm, Advisor, User, AuthorisedRepresentative, FirmData
from django.views.generic import CreateView, View, TemplateView
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponseRedirect
from ..base import LegalView
from django.views.generic.edit import ProcessFormView
from django.contrib.contenttypes.models import ContentType


__all__ = ["InviteLegalView", "AuthorisedRepresentativeSignUp", 'FirmDataView', "EmailConfirmationView", 'NewConfirmation',
           'AdminInviteSupervisorView', 'AdminInviteAdvisorView']


class AuthorisedRepresentativeProfileForm(forms.ModelForm):
    medicare_number = forms.CharField(
        max_length=20,
        label=mark_safe('Medicare # <span class="security-icon"></span>'),
        help_text="Bank-Level Security"
    )

    user = forms.CharField(required=False)

    class Meta:
        model = AuthorisedRepresentative
        fields = PERSONAL_DATA_FIELDS + ('letter_of_authority', 'betasmartz_agreement', 'firm', 'user')

        widgets = PERSONAL_DATA_WIDGETS


class AuthorisedRepresentativeUserForm(BetaSmartzGenericUSerSignupForm):
    user_profile_type = "authorised_representative"

    class Meta:
        model = User
        fields = ('email', 'first_name',  'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AuthorisedRepresentativeUserForm, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.profile = getattr(kwargs['instance'], self.user_profile_type, None)
            profile_kwargs['instance'] = self.profile
        self.profile_form = AuthorisedRepresentativeProfileForm(*args, **profile_kwargs)
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
        user = super(AuthorisedRepresentativeUserForm, self).save(*args, **kw)
        self.profile = self.profile_form.save(commit=False)
        self.profile.user = user
        self.profile.save()
        self.profile.send_confirmation_email()
        return user

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class AuthorisedRepresentativeSignUp(CreateView):
    template_name = "registration/firm_form.html"
    form_class = AuthorisedRepresentativeUserForm
    success_url = "/firm/login"

    def __init__(self, *args, **kwargs):
        self.firm = None
        super(AuthorisedRepresentativeSignUp, self).__init__(*args, **kwargs)

    def get_success_url(self):
        messages.info(self.request, SUCCESS_MESSAGE)
        return super(AuthorisedRepresentativeSignUp, self).get_success_url()

    def dispatch(self, request, *args, **kwargs):
        token = kwargs["token"]

        try:
            firm = Firm.objects.get(token=token)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm
        response = super(AuthorisedRepresentativeSignUp, self).dispatch(request, *args, **kwargs)

        if hasattr(response, 'context_data'):
            response.context_data["firm"] = self.firm
            response.context_data["sign_up_type"] = "legal representative account"
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
            invitation_type = AUTHORIZED_REPRESENTATIVE
            response.context_data["invitation_type"] = invitation_type
            response.context_data["invite_url"] = firm.get_invite_url(invitation_type)
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response


class AdminInviteAdvisorView(CreateView, AdminView):
    form_class = EmailInviteForm
    template_name = 'admin/betasmartz/legal_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(AdminInviteAdvisorView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = Firm.objects.get(pk=kwargs["pk"])
            invitation_type = INVITATION_ADVISOR
            response.context_data["firm"] = firm
            response.context_data["invitation_type"] = invitation_type
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["invite_url"] = firm.get_invite_url(invitation_type)
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
                                                                              inviter_id=firm.pk,
                                                                              inviter_type=firm.content_type,
                                                                              )
        return response


class AdminInviteSupervisorView(CreateView, AdminView):
    form_class = EmailInviteForm
    template_name = 'admin/betasmartz/legal_invite.html'

    def get_success_url(self):
        messages.info(self.request, "Invite sent successfully!")
        return self.request.get_full_path()

    def dispatch(self, request, *args, **kwargs):
        response = super(AdminInviteSupervisorView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            firm = Firm.objects.get(pk=kwargs["pk"])
            invitation_type = INVITATION_SUPERVISOR
            response.context_data["firm"] = firm
            response.context_data["invitation_type"] = invitation_type
            response.context_data["invite_type"] = INVITATION_TYPE_DICT[str(invitation_type)].title()
            response.context_data["next"] = request.GET.get("next", None)
            response.context_data["invite_url"] = firm.get_invite_url(invitation_type)
            response.context_data["invites"] = EmailInvitation.objects.filter(invitation_type=invitation_type,
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


class EmailConfirmationView(View):

    def get(self, request, *args, **kwargs):

        token = kwargs.get("token")
        _type = kwargs.get("type")

        try:
            object_class = ContentType.objects.get(pk=_type).model_class()
        except ObjectDoesNotExist:
            raise Http404("Page not found")

        try:
            db_object = object_class.objects.get(confirmation_key=token)
        except ObjectDoesNotExist:
            db_object = None

        if db_object is None:
            messages.error(request, "Bad confirmation code")
        else:
            if db_object.is_confirmed:
                messages.error(request, "{0} already confirmed".format(object_class.__name__))
            else:
                messages.info(request, "You email have been confirmed, you can login in")
                db_object.is_confirmed = True

            db_object.confirmation_key = None
            db_object.save()

        return HttpResponseRedirect('/login')


class NewConfirmation(TemplateView):
    template_name = 'registration/confirmation.html'

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        account_types = ('advisor', 'authorised_representative', 'supervisor', 'client')

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.error(request, "Account not found")
            return HttpResponseRedirect("/login")

        confirmations = 0

        for _type in account_types:
            if hasattr(user, _type):
                profile = getattr(user, _type)
                if profile.is_confirmed:
                    pass
                else:
                    profile.send_confirmation_email()
                    confirmations += 1

        if not confirmations:
            messages.error(request, "Account already confirmed")
            return HttpResponseRedirect("/login")

        messages.info(request, "The new confirmation email has been sent")
        return HttpResponseRedirect('/login')
