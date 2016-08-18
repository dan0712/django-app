from support.models import SupportRequest

__author__ = 'cristian'

from advisors.models import ChangeDealerGroup, SingleInvestorTransfer, BulkInvestorTransfer
from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView
from main.models import Advisor, User, Section, Firm
from main.constants import SUCCESS_MESSAGE, PERSONAL_DATA_FIELDS
from main.forms import PERSONAL_DATA_WIDGETS, BetaSmartzGenericUserSignupForm
from ..base import AdvisorView

__all__ = ["AdvisorSignUpView", "AdvisorChangeDealerGroupView", "AdvisorChangeDealerGroupUpdateView",
           "AdvisorSingleInvestorTransferView", "AdvisorSingleInvestorTransferUpdateView",
           "AdvisorBulkInvestorTransferView", "AdvisorBulkInvestorTransferUpdateView"]


class AdvisorProfile(forms.ModelForm):
    medicare_number = forms.CharField(
        max_length=20,
        label=mark_safe('Medicare # <span class="security-icon"></span>'),
        help_text="Bank-Level Security"
    )

    user = forms.CharField(required=False)

    class Meta:
        model = Advisor
        fields = PERSONAL_DATA_FIELDS + ('letter_of_authority', 'betasmartz_agreement', 'firm', 'user')

        widgets = PERSONAL_DATA_WIDGETS


class AdvisorUserForm(BetaSmartzGenericUserSignupForm):
    user_profile_type = "advisor"

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(AdvisorUserForm, self).__init__(*args, **kwargs)
        profile_kwargs = kwargs.copy()
        if 'instance' in kwargs:
            self.profile = getattr(kwargs['instance'], self.user_profile_type, None)
            profile_kwargs['instance'] = self.profile
        self.profile_form = AdvisorProfile(*args, **profile_kwargs)
        self.fields.update(self.profile_form.fields)
        self.initial.update(self.profile_form.initial)

        self.field_sections = [{"fields": ('first_name', 'middle_name', 'last_name', 'email', 'password',
                                           'confirm_password', 'date_of_birth', 'gender', 'phone_num'),
                                "header": "Information to establish your account"},
                               {"fields": ('medicare_number',),
                                "header": "Identity verification",
                                "detail": "We use your Medicare number to verify your identity and protect "
                                          "against fraud."},
                               {"fields": ('letter_of_authority',),
                                "header": "Authorization",
                                "detail": "BetaSmartz requires a Letter of Authority (PDF) from the new Dealer Group"
                                          " which authorises you to act on their behalf. This letter must"
                                          " be provided by the Dealer Group on Dealer Group company letterhead."}
                               ]

    def save(self, *args, **kw):
        user = super(AdvisorUserForm, self).save(*args, **kw)
        self.profile = self.profile_form.save(commit=False)
        self.profile.user = user
        self.profile.save()
        self.profile.send_confirmation_email()
        return user

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class AdvisorSignUpView(CreateView):
    template_name = "registration/firm_form.html"
    form_class = AdvisorUserForm
    success_url = reverse_lazy('login')

    def __init__(self, *args, **kwargs):
        self.firm = None
        super(AdvisorSignUpView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        messages.info(self.request, SUCCESS_MESSAGE)
        return super(AdvisorSignUpView, self).get_success_url()

    def dispatch(self, request, *args, **kwargs):
        token = kwargs["token"]

        try:
            firm = Firm.objects.get(token=token)
        except ObjectDoesNotExist:
            raise Http404()

        self.firm = firm

        response = super(AdvisorSignUpView, self).dispatch(request, *args, **kwargs)

        if hasattr(response, 'context_data'):
            response.context_data["firm"] = self.firm
            response.context_data["sign_up_type"] = "advisor account"
        return response


class ChangeDealerGroupForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={"disabled": True}),
                                             queryset=None)

    class Meta:
        model = ChangeDealerGroup
        fields = ("advisor", "old_firm", "new_firm", "work_phone", "new_email", "letter_new_group",
                  "letter_previous_group", "signature", "clients")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        if "data" in kwargs:
            q = QueryDict('', mutable=True)
            q.update(kwargs["data"])
            initial = dict()
            initial["advisor"] = str(kwargs["initial"]["advisor"].pk)
            initial["old_firm"] = str(kwargs["initial"]["old_firm"].pk)
            q.update(initial)
            kwargs["data"] = q
        super(ChangeDealerGroupForm, self).__init__(*args, **kwargs)

        self.field_sections = [{"fields": ('new_firm', 'work_phone', 'new_email'),
                                "header": "New arrangements"},
                               {"fields": ('clients',),
                                "header": "Your current investors"},
                               {"fields": ('letter_previous_group',),
                                "header": "Previous Dealer Group Release Authorization",
                                "detail": mark_safe("A letter from your previous Dealer Group authorising the release "
                                                    "of your current investors. A template of this letter has been supplied, "
                                                    "This letter must be provided on the previous Dealer Group's "
                                                    "company letterhead. <a target='_blank' href='/static/docs/previous_dealer_group_release_authorization.pdf'>Example</a>")},
                               {"fields": ('letter_new_group',),
                                "header": "New Dealer Group Acceptance Authorization",
                                "detail": mark_safe("A letter from the new Dealer Group accepting the transfer of your "
                                                    "current investors. A template of this letter has been supplied. This letter"
                                                    "must be provided on the new Dealer Group's company letterhead. <a target='_blank' href='/static/docs/new_dealer_group_acceptance_authorization.pdf'>Example</a>")},
                               {"fields": ('signature',),
                                "header": "Advisor Signature",
                                "detail": mark_safe(
                                    "Please upload a signature approval by an Authorised Signatory of the new Dealer Group. <a target='_blank' href='/static/docs/advisor_signature_change_dealer_group.pdf'>Example</a>"),
                                }
                               ]
        self.fields["new_firm"].queryset = Firm.objects.exclude(pk=self.initial["old_firm"].pk)
        self.fields["clients"].queryset = self.initial["advisor"].clients

    def clean_new_email(self):
        email = self.cleaned_data["new_email"]
        if User.objects.exclude(pk=self.initial["advisor"].user.pk).filter(email=email).count():
            self._errors['new_email'] = "User with this email already exists"

        return email

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class AdvisorChangeDealerGroupView(AdvisorView, CreateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = ChangeDealerGroupForm

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorChangeDealerGroupView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Change of dealer group"
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Change of dealer group submitted successfully")
        return super(AdvisorChangeDealerGroupView, self).get_success_url()

    def get_initial(self):
        return {"advisor": self.advisor, "old_firm": self.advisor.firm, "new_email": self.advisor.email}

    def dispatch(self, request, *args, **kwargs):

        try:
            user = SupportRequest.target_user(request)
            cdg = ChangeDealerGroup.objects.exclude(approved=True).get(advisor=user.advisor)
            return HttpResponseRedirect("/advisor/support/forms/change/firm/update/{0}".format(cdg.pk))
        except ObjectDoesNotExist:
            return super(AdvisorChangeDealerGroupView, self).dispatch(request, *args, **kwargs)


class AdvisorChangeDealerGroupUpdateView(AdvisorView, UpdateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = ChangeDealerGroupForm
    model = ChangeDealerGroup

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorChangeDealerGroupUpdateView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Change of dealer group"
        ctx_data["object"] = self.object
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Change of dealer group submitted successfully")
        return super(AdvisorChangeDealerGroupUpdateView, self).get_success_url()

    def get_initial(self):
        return {"advisor": self.advisor, "old_firm": self.advisor.firm, "new_email": self.advisor.email}


class SingleInvestorTransferForm(forms.ModelForm):
    class Meta:
        model = SingleInvestorTransfer
        fields = ("from_advisor", "to_advisor", "investor", "signatures",)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        if "data" in kwargs:
            q = QueryDict('', mutable=True)
            q.update(kwargs["data"])
            initial = dict()
            initial["from_advisor"] = str(kwargs["initial"]["from_advisor"].pk)
            q.update(initial)
            kwargs["data"] = q

        super(SingleInvestorTransferForm, self).__init__(*args, **kwargs)

        self.field_sections = [{"fields": ('to_advisor',),
                                "header": "To Advisor"},
                               {"fields": ('investor',),
                                "header": "Investor"},
                               {"fields": ('signatures',),
                                "header": "Signatures",
                                "detail": mark_safe("Signatures of the investor and the previous advisor: if this is "
                                                    "for a Joint Account the signature of the second  investor "
                                                    "is required. <a target='_blank' href='/static/docs/advisor_single_transferer_signatures.pdf'>Example</a>")},
                               ]

        self.fields["investor"].queryset = self.initial["from_advisor"].clients
        self.fields["to_advisor"].queryset = Advisor.objects.filter(firm=self.initial["from_advisor"].firm)

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class AdvisorSingleInvestorTransferView(AdvisorView, CreateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = SingleInvestorTransferForm

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorSingleInvestorTransferView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Single investor transfer"
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Single investor transfer submitted successfully")
        return super(AdvisorSingleInvestorTransferView, self).get_success_url()

    def get_initial(self):
        return {"from_advisor": self.advisor}

    def dispatch(self, request, *args, **kwargs):

        try:
            user = SupportRequest.target_user(request)
            sit = SingleInvestorTransfer.objects.exclude(approved=True).get(from_advisor=user.advisor)
            return HttpResponseRedirect("/advisor/support/forms/transfer/single/update/{0}".format(sit.pk))
        except ObjectDoesNotExist:
            return super(AdvisorSingleInvestorTransferView, self).dispatch(request, *args, **kwargs)


class AdvisorSingleInvestorTransferUpdateView(AdvisorView, UpdateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = SingleInvestorTransferForm
    model = SingleInvestorTransfer

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorSingleInvestorTransferUpdateView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Single investor transfer"
        ctx_data["object"] = self.object
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Single investor transfer submitted successfully")
        return super(AdvisorSingleInvestorTransferUpdateView, self).get_success_url()

    def get_initial(self):
        return {"from_advisor": self.advisor}


class BulkInvestorTransferForm(forms.ModelForm):
    class Meta:
        model = BulkInvestorTransfer
        fields = ("from_advisor", "to_advisor", "investors", "signatures",)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        if "data" in kwargs:
            q = QueryDict('', mutable=True)
            q.update(kwargs["data"])
            initial = dict()
            initial["from_advisor"] = str(kwargs["initial"]["from_advisor"].pk)
            q.update(initial)
            kwargs["data"] = q

        super(BulkInvestorTransferForm, self).__init__(*args, **kwargs)

        self.field_sections = [{"fields": ('to_advisor',),
                                "header": "To Advisor"},
                               {"fields": ('investors',),
                                "detail": "You can select 2 or more investors for transfer",
                                "header": "Investors"},
                               {"fields": ('signatures',),
                                "header": "Signatures",
                                "detail": mark_safe("Signatures of the previous advisor and new advisor."
                                                    " <a target='_blank' href='/static/docs/advisor_bulk_transferer_signatures.pdf'>Example</a>")},
                               ]

        self.fields["investors"].queryset = self.initial["from_advisor"].clients
        self.fields["to_advisor"].queryset = Advisor.objects.filter(firm=self.initial["from_advisor"].firm)

    def clean_investors(self):
        investors = self.cleaned_data["investors"]
        if len(investors) < 2:
            self._errors["investors"] = "Please select 2 or more investors"
        return investors

    @property
    def sections(self):
        for section in self.field_sections:
            yield Section(section, self)


class AdvisorBulkInvestorTransferView(AdvisorView, CreateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = BulkInvestorTransferForm

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorBulkInvestorTransferView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Bulk investor transfer"
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Bulk investor transfer submitted successfully")
        return super(AdvisorBulkInvestorTransferView, self).get_success_url()

    def get_initial(self):
        return {"from_advisor": self.advisor}

    def dispatch(self, request, *args, **kwargs):

        try:
            user = SupportRequest.target_user(request)
            sit = BulkInvestorTransfer.objects.exclude(approved=True).get(from_advisor=user.advisor)
            return HttpResponseRedirect("/advisor/support/forms/transfer/bulk/update/{0}".format(sit.pk))
        except ObjectDoesNotExist:
            return super(AdvisorBulkInvestorTransferView, self).dispatch(request, *args, **kwargs)


class AdvisorBulkInvestorTransferUpdateView(AdvisorView, UpdateView):
    template_name = "advisor/form-firm.html"
    success_url = "/advisor/support/forms"
    form_class = BulkInvestorTransferForm
    model = BulkInvestorTransfer

    def get_context_data(self, **kwargs):
        ctx_data = super(AdvisorBulkInvestorTransferUpdateView, self).get_context_data(**kwargs)
        ctx_data["form_name"] = "Bulk investor transfer"
        ctx_data["object"] = self.object
        return ctx_data

    def get_success_url(self):
        messages.success(self.request, "Bulk investor transfer submitted successfully")
        return super(AdvisorBulkInvestorTransferUpdateView, self).get_success_url()

    def get_initial(self):
        return {"from_advisor": self.advisor}
