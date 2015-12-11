import json
import uuid
from datetime import date
from json.decoder import JSONDecodeError

from django import forms
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, _, \
    UserManager, timezone, \
    send_mail
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, ValidationError, MinValueValidator, MaxValueValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_localflavor_au.models import AUPhoneNumberField, AUStateField, AUPostCodeField
from main.slug import unique_slugify
from numpy import array
from .fields import ColorField


def validate_agreement(value):
    if value is False:
        raise ValidationError("You must accept the agreement to continue.")


SUCCESS_MESSAGE = "Your application has been submitted successfully, you will receive a confirmation email" \
                  " following a BetaSmartz approval."

INVITATION_PENDING = 0
INVITATION_SUBMITTED = 1
INVITATION_ACTIVE = 3
INVITATION_CLOSED = 4

EMAIL_INVITATION_STATUSES = (
    (INVITATION_PENDING, 'Pending'), (INVITATION_SUBMITTED, 'Submitted'),
    (INVITATION_ACTIVE, 'Active'), (INVITATION_CLOSED, 'Closed'))

INVITATION_ADVISOR = 0
AUTHORIZED_REPRESENTATIVE = 1
INVITATION_SUPERVISOR = 2
INVITATION_CLIENT = 3
INVITATION_TYPE_CHOICES = (
    (INVITATION_ADVISOR, "Advisor"),
    (AUTHORIZED_REPRESENTATIVE, 'Authorised representative'),
    (INVITATION_CLIENT, 'Client'), (INVITATION_SUPERVISOR, 'Supervisor'))

INVITATION_TYPE_DICT = {
    str(INVITATION_ADVISOR): "advisor",
    str(AUTHORIZED_REPRESENTATIVE): "authorised_representative",
    str(INVITATION_CLIENT): "client",
    str(INVITATION_SUPERVISOR): "supervisor"
}

TFN_YES = 0
TFN_NON_RESIDENT = 1
TFN_CLAIM = 2
TFN_DONT_WANT = 3

TFN_CHOICES = (
    (TFN_YES, "Yes"),
    (TFN_NON_RESIDENT, "I am a non-resident of Australia"),
    (TFN_CLAIM, "I want to claim an exemption"),
    (TFN_DONT_WANT, "I do not want to quote a Tax File Number or exemption"),)

Q1 = "What was the name of your primary school?"
Q2 = "What is your mother's maiden name?"
Q3 = "What was the name of your first pet?"
Q4 = "What was your first car?"
Q5 = "What was your favourite subject at school?"
Q6 = "In what month was your father born?"

QUESTION_1_CHOICES = ((Q1, Q1), (Q2, Q2), (Q3, Q3))

QUESTION_2_CHOICES = ((Q4, Q4), (Q5, Q5), (Q6, Q6))

PERSONAL_DATA_FIELDS = ('date_of_birth', 'gender', 'address_line_1',
                        'address_line_2', 'city', 'state', 'post_code',
                        'phone_number', 'security_question_1',
                        "security_question_2", "security_answer_1",
                        "security_answer_2", 'medicare_number')

PERSONAL_DATA_WIDGETS = {
    "gender": forms.RadioSelect(),
    "date_of_birth": forms.TextInput(attrs={"placeholder": "DD-MM-YYYY"}),
    'address_line_1':
        forms.TextInput(attrs={"placeholder": "House name, Unit/House number"}),
    "address_line_2": forms.TextInput(
        attrs={"placeholder": "Street address"})
}

ALLOCATION = "ALLOCATION"
DEPOSIT = "DEPOSIT"
WITHDRAWAL = "WITHDRAWAL"
FEE = "FEE"
REBALANCE = "REBALANCE"
MARKET_CHANGE = "MARKET_CHANGE"

TRANSACTION_CHOICES = ((REBALANCE, 'REBALANCE'), (ALLOCATION, "ALLOCATION"),
                       (DEPOSIT, "DEPOSIT"), (WITHDRAWAL, 'WITHDRAWAL'),
                       (MARKET_CHANGE, "MARKET_CHANGE"))

PENDING = 'PENDING'
EXECUTED = 'EXECUTED'

TRANSACTION_STATUS_CHOICES = (('PENDING', 'PENDING'), ('EXECUTED', 'EXECUTED'))


class BetaSmartzAgreementForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(BetaSmartzAgreementForm, self).clean()
        if not (cleaned_data["betasmartz_agreement"] is True):
            self._errors['betasmartz_agreement'] = mark_safe(
                '<ul class="errorlist">'
                '<li>You must accept the BetaSmartz\'s agreement'
                ' to continue.</li></ul>')

        return cleaned_data


class BetaSmartzGenericUSerSignupForm(BetaSmartzAgreementForm):
    confirm_password = forms.CharField(max_length=50,
                                       widget=forms.PasswordInput())
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    user_profile_type = None

    def clean(self):
        cleaned_data = super(BetaSmartzGenericUSerSignupForm, self).clean()
        self._validate_unique = False

        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')

        if password1 and (password1 != password2):
            self._errors['confirm_password'] = mark_safe(
                '<ul class="errorlist"><li>Passwords don\'t match.</li></ul>')

        # check if user already exist
        try:
            user = User.objects.get(email=cleaned_data.get('email'))
        except ObjectDoesNotExist:
            user = None

        if (user is not None) and (not user.prepopulated):
            # confirm password
            if not user.check_password(password1):
                self._errors['email'] = mark_safe(
                    u'<ul class="errorlist"><li>User already exists</li></ul>')
            else:
                if hasattr(user, self.user_profile_type):
                    rupt = self.user_profile_type.replace("_", " ")
                    self._errors['email'] = mark_safe(
                        u'<ul class="errorlist"><li>User already has an'
                        u' {0} account</li></ul>'.format(rupt))

        cleaned_data["password"] = make_password(password1)
        return cleaned_data

    def save(self, *args, **kw):
        # check if user already exist
        try:
            self.instance = User.objects.get(
                email=self.cleaned_data.get('email'))
        except ObjectDoesNotExist:
            pass
        instance = super(BetaSmartzGenericUSerSignupForm, self).save(*args, **kw)
        instance.prepopulated = False
        instance.password = self.cleaned_data["password"]
        instance.save()
        return instance


class Section:
    def __init__(self, section, form):
        self.header = section.get("header", "")
        self.detail = section.get("detail", None)
        self.css_class = section.get("css_class", None)
        self.fields = []
        for field_name in section["fields"]:
            self.fields.append(form[field_name])


YES_NO = ((False, "No"), (True, "Yes"))


class NeedApprobation(models.Model):
    class Meta:
        abstract = True

    is_accepted = models.BooleanField(default=False, editable=False)

    def approve(self):
        if self.is_accepted is True:
            return
        self.is_accepted = True
        self.save()
        self.send_approve_email()

    def send_approve_email(self):
        account_type = self._meta.verbose_name

        subject = "Your BetaSmartz new {0} account have been approved".format(
            account_type)

        context = {
            'subject': subject,
            'account_type': account_type,
            'firm_name': self.firm.name
        }

        send_mail(subject,
                  '',
                  None,
                  [self.email],
                  html_message=render_to_string('email/approve_account.html',
                                                context))


class NeedConfirmation(models.Model):
    class Meta:
        abstract = True

    confirmation_key = models.CharField(max_length=36,
                                        null=True,
                                        blank=True,
                                        editable=False)
    is_confirmed = models.BooleanField(default=False, editable=True)

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self).pk

    def get_confirmation_url(self):
        if self.is_confirmed is False:
            if self.confirmation_key is None:
                self.confirmation_key = str(uuid.uuid4())
                self.save()

        if self.is_confirmed or (self.confirmation_key is None):
            return None

        return settings.SITE_URL + "/confirm_email/{0}/{1}".format(
            self.content_type, self.confirmation_key)

    def send_confirmation_email(self):
        account_type = self._meta.verbose_name

        subject = "BetaSmartz new {0} account confirmation".format(
            account_type)

        context = {
            'subject': subject,
            'account_type': account_type,
            'confirmation_url': self.get_confirmation_url(),
            'firm_name': self.firm.name
        }

        send_mail(
            subject,
            '',
            None,
            [self.email],
            html_message=render_to_string('email/confirmation.html', context))


class PersonalData(models.Model):
    class Meta:
        abstract = True

    date_of_birth = models.DateField(verbose_name="Date of birth", null=True)
    gender = models.CharField(max_length=20,
                              default="Male",
                              choices=(("Male", "Male"), ("Female", "Female")))
    address_line_1 = models.CharField(max_length=255, default="")
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, default="", verbose_name="City/Town")
    state = AUStateField(default='QLD')
    post_code = AUPostCodeField(null=True)
    phone_number = AUPhoneNumberField(null=True)
    security_question_1 = models.CharField(max_length=255,
                                           default="",
                                           choices=QUESTION_1_CHOICES)
    security_question_2 = models.CharField(max_length=255,
                                           default="",
                                           choices=QUESTION_2_CHOICES)
    security_answer_1 = models.CharField(max_length=255, verbose_name="Answer", default="")
    security_answer_2 = models.CharField(max_length=255, verbose_name="Answer", default="")
    medicare_number = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.user.first_name + " - " + self.firm.name

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def phone(self):
        return self.work_phone[0:4] + "-" + self.work_phone[
                                            4:7] + "-" + self.work_phone[7:10]

    @property
    def email(self):
        return self.user.email


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """

    first_name = models.CharField(_('first name'), max_length=30)
    middle_name = models.CharField(_('middle name(s)'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30)
    username = models.CharField(max_length=30, editable=False, default='')
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        })

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    prepopulated = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        " Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Firm(models.Model):
    name = models.CharField(max_length=255)
    dealer_group_number = models.CharField(max_length=50,
                                           null=True,
                                           blank=True)
    slug = models.CharField(max_length=100, editable=False, unique=True)
    logo_url = models.ImageField(verbose_name="White logo",
                                 null=True,
                                 blank=True)
    knocked_out_logo_url = models.ImageField(verbose_name="Colored logo",
                                             null=True,
                                             blank=True)
    client_agreement_url = models.FileField(
        verbose_name="Client Agreement (PDF)",
        null=True,
        blank=True)
    form_adv_part2_url = models.FileField(verbose_name="Form Adv",
                                          null=True,
                                          blank=True)
    token = models.CharField(max_length=36, editable=False)
    fee = models.PositiveIntegerField(default=0)
    can_use_ethical_portfolio = models.BooleanField(default=True)

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):

        if self.pk is None:
            self.token = str(uuid.uuid4())

        # reset slug with name changes
        if self.pk is not None:
            orig = Firm.objects.get(pk=self.pk)
            if orig.name != self.name:
                self.slug = None

        if not self.slug:
            unique_slugify(self, self.name, slug_field_name="slug")
        else:
            unique_slugify(self, self.slug, slug_field_name="slug")

        super(Firm, self).save(force_insert, force_update, using,
                               update_fields)

    @property
    def white_logo(self):

        if self.logo_url is None:
            return settings.STATIC_URL + 'images/white_logo.png'
        elif not self.logo_url.name:
            return settings.STATIC_URL + 'images/white_logo.png'

        return settings.MEDIA_URL + self.logo_url.name

    @property
    def colored_logo(self):

        if self.knocked_out_logo_url is None:
            return settings.STATIC_URL + 'images/colored_logo.png'
        elif not self.knocked_out_logo_url.name:
            return settings.STATIC_URL + 'images/colored_logo.png'

        return settings.MEDIA_URL + self.knocked_out_logo_url.name

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self).pk

    @property
    def authorised_representative_form_url(self):
        if self.token is None:
            return None
        return settings.SITE_URL + "/" + self.token + "/legal_signup"

    @property
    def supervisor_invite_url(self):
        if self.token is None:
            return None
        return settings.SITE_URL + "/" + self.token + "/supervisor_signup"

    @property
    def advisor_invite_url(self):
        if self.token is None:
            return None
        return settings.SITE_URL + "/" + self.token + "/advisor_signup"

    @staticmethod
    def get_inviter_type():
        return "firm"

    def get_inviter_name(self):
        return self.name

    def get_invite_url(self, application_type, email):
        if application_type == AUTHORIZED_REPRESENTATIVE:
            return self.authorised_representative_form_url
        if application_type == INVITATION_ADVISOR:
            return self.advisor_invite_url
        if application_type == INVITATION_SUPERVISOR:
            return self.supervisor_invite_url

    def __str__(self):
        return self.name


class FirmData(models.Model):
    class Meta:
        verbose_name = "Firm detail"

    firm = models.OneToOneField(Firm, related_name='firm_details')
    afsl_asic = models.CharField("AFSL/ASIC number", max_length=50)
    afsl_asic_document = models.FileField("AFSL/ASIC doc.")
    office_address_line_1 = models.CharField("Office address 1",
                                             max_length=255)
    office_address_line_2 = models.CharField("Office address 2",
                                             max_length=255,
                                             null=True,
                                             blank=True)
    office_state = AUStateField()
    office_city = models.CharField(max_length=255)
    office_post_code = AUPostCodeField()
    postal_address_line_1 = models.CharField("Postal address 1",
                                             max_length=255)
    postal_address_line_2 = models.CharField("Postal address 2",
                                             max_length=255,
                                             null=True,
                                             blank=True)
    postal_state = AUStateField()
    same_address = models.BooleanField(default=False)
    postal_city = models.CharField(max_length=255)
    postal_post_code = AUPostCodeField()
    daytime_phone_number = AUPhoneNumberField()
    mobile_phone_number = AUPhoneNumberField()
    fax_number = AUPhoneNumberField()
    alternate_email_address = models.EmailField("Email address",
                                                null=True,
                                                blank=True)
    last_change = models.DateField(auto_now=True)
    fee_bank_account_name = models.CharField('Name', max_length=100)
    fee_bank_account_branch_name = models.CharField('Branch name',
                                                    max_length=100)
    fee_bank_account_bsb_number = models.CharField('BSB number', max_length=20)
    fee_bank_account_number = models.CharField('Account number', max_length=20)
    fee_bank_account_holder_name = models.CharField('Account holder',
                                                    max_length=100)
    australian_business_number = models.CharField("ABN", max_length=20)


class Advisor(NeedApprobation, NeedConfirmation, PersonalData):
    user = models.OneToOneField(User, related_name="advisor")
    token = models.CharField(max_length=36, null=True, editable=False)
    firm = models.ForeignKey(Firm, related_name="advisors")
    letter_of_authority = models.FileField()
    work_phone = AUPhoneNumberField(null=True)
    betasmartz_agreement = models.BooleanField()

    @property
    def dashboard_url(self):
        return "/advisor/summary"

    @property
    def clients(self):
        return self.all_clients.filter(user__prepopulated=False)

    @property
    def firm_colored_logo(self):
        return self.firm.knocked_out_logo_url

    def get_invite_url(self, invitation_type=None, email=None):
        if self.token is None:
            return ''

        try:
            user = User.objects.get(email=email, prepopulated=True)
        except ObjectDoesNotExist:
            user = None

        invitation_url = settings.SITE_URL + "/" + self.firm.slug + "/client/signup/" + self.token

        if user:
            invitation_url += "/" + str(user.pk) + "/" + user.client.accounts_all.first().token
        return invitation_url

    @staticmethod
    def get_inviter_type():
        return "advisor"

    @property
    def households(self):
        all_households = list(self.primary_account_groups.all()) + list(self.secondary_account_groups.all())
        active_households = []
        for h in all_households:
            if list(h.accounts.all()):
                active_households.append(h)

        return active_households

    @property
    def total_balance(self):
        b = 0
        for ag in self.households:
            b += ag.total_balance

        return b

    @property
    def total_account_groups(self):
        return len(self.households)

    @property
    def average_balance(self):
        if self.total_account_groups > 0:
            return self.total_balance / self.total_account_groups
        return 0

    def get_inviter_name(self):
        return self.user.get_full_name()

    def save(self, *args, **kw):
        send_confirmation_mail = False
        if self.pk is not None:
            orig = Advisor.objects.get(pk=self.pk)
            if (orig.is_accepted != self.is_accepted) and (
                        self.is_accepted is True):
                send_confirmation_mail = True

        super(Advisor, self).save(*args, **kw)
        if send_confirmation_mail and (self.confirmation_key is not None):
            self.user.email_user(
                "BetaSmartz advisor account confirmation",
                "You advisor account have been approved, "
                "please confirm your email here: "
                "{site_url}/advisor/confirm_email/{confirmation_key}/"
                " \n\n\n  The BetaSmartz Team".format(
                    confirmation_key=self.confirmation_key,
                    site_url=settings.SITE_URL))


class AuthorisedRepresentative(NeedApprobation, NeedConfirmation, PersonalData
                               ):
    user = models.OneToOneField(User, related_name='authorised_representative')
    firm = models.ForeignKey(Firm, related_name='authorised_representatives')
    letter_of_authority = models.FileField()
    betasmartz_agreement = models.BooleanField()


class AccountGroup(models.Model):
    advisor = models.ForeignKey(Advisor, related_name="primary_account_groups")
    secondary_advisors = models.ManyToManyField(
        Advisor,
        related_name='secondary_account_groups')
    name = models.CharField(max_length=100)

    @property
    def accounts(self):
        return self.accounts_all.filter(confirmed=True, primary_owner__user__prepopulated=False)

    @property
    def total_balance(self):
        b = 0
        for a in self.accounts.all():
            b += a.total_balance
        return b

    @property
    def total_returns(self):
        return 0

    @property
    def allocation(self):
        return 0

    @property
    def stock_balance(self):
        b = 0
        for account in self.accounts.all():
            b += account.stock_balance
        return b

    @property
    def bond_balance(self):
        b = 0
        for account in self.accounts.all():
            b += account.bond_balance
        return b

    @property
    def stocks_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.stock_balance / self.total_balance * 100)))

    @property
    def bonds_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.bond_balance / self.total_balance * 100)))

    @property
    def on_track(self):
        on_track = True
        for account in self.accounts.all():
            on_track = on_track and account.on_track
        return on_track

    @property
    def since(self):
        min_created_at = self.accounts.first().created_at

        for account in self.accounts.all():
            if min_created_at > account.created_at:
                min_created_at = account.created_at

        return min_created_at

    def __str__(self):
        return self.name


PERSONAL_ACCOUNT = "PERSONAL"

ACCOUNT_TYPES = ((PERSONAL_ACCOUNT, "Personal Account"),)

JOINT_ACCOUNT = "joint_account"
TRUST_ACCOUNT = "trust_account"

ACCOUNT_CLASSES = ((JOINT_ACCOUNT, "Personal Account"),
                   (TRUST_ACCOUNT, "SMSF/Trust Account"))


class ClientAccount(models.Model):
    account_group = models.ForeignKey(AccountGroup,
                                      related_name="accounts_all",
                                      null=True)
    custom_fee = models.PositiveIntegerField(default=0)
    account_class = models.CharField(max_length=20, choices=ACCOUNT_CLASSES, default=TRUST_ACCOUNT)

    account_name = models.CharField(max_length=255, default=PERSONAL_ACCOUNT)
    primary_owner = models.ForeignKey('Client', related_name="accounts_all")
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=36, editable=False)
    confirmed = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.token = str(uuid.uuid4())

        return super(ClientAccount, self).save(force_insert, force_update, using, update_fields)

    def remove_from_group(self):
        old_group = self.account_group

        # get personal group or create it
        group_name = "{0}".format(self.primary_owner.full_name)
        groups = AccountGroup.objects.filter(
            name=group_name,
            advisor=self.primary_owner.advisor)
        if groups:
            group = groups[0]
        else:
            group = AccountGroup(name=group_name,
                                 advisor=self.primary_owner.advisor)
            group.save()

        self.account_group = group
        self.save()
        self.primary_owner.rebuild_secondary_advisors()

        if old_group:
            if old_group.accounts.count() == 0:
                old_group_name = old_group.name
                # delete account group
                old_group.delete()
                return old_group_name

    def add_to_account_group(self, account_group):
        old_account_group = self.account_group
        self.account_group = account_group
        self.save()

        if old_account_group:
            if old_account_group.accounts.count() == 0:
                # delete account group
                old_account_group.delete()

        self.primary_owner.rebuild_secondary_advisors()

    @property
    def fee(self):
        if self.custom_fee != 0:
            return self.custom_fee + Platform.objects.first().fee
        else:
            return self.primary_owner.advisor.firm.fee + Platform.objects.first(
            ).fee

    @property
    def fee_fraction(self):
        return self.fee / 1000

    @property
    def name(self):
        """if self.account_name == PERSONAL_ACCOUNT:
            return "{0}'s Personal Account".format(
                self.primary_owner.user.first_name)"""

        return "{0}'s {1}".format(
            self.primary_owner.user.first_name, self.get_account_class_display())

    @property
    def total_balance(self):
        b = 0
        for goal in self.goals.all():
            b += goal.total_balance
        return b

    @property
    def stock_balance(self):
        b = 0
        for goal in self.goals.all():
            b += goal.stock_balance
        return b

    @property
    def bond_balance(self):
        b = 0
        for goal in self.goals.all():
            b += goal.bond_balance
        return b

    @property
    def total_returns(self):
        return 0

    @property
    def stocks_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.stock_balance / self.total_balance * 100)))

    @property
    def bonds_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.bond_balance / self.total_balance * 100)))

    @property
    def owners(self):
        return self.primary_owner.full_name

    @property
    def account_type_name(self):
        for at in ACCOUNT_TYPES:
            if at[0] == self.account_name:
                return at[1]

    @property
    def on_track(self):
        on_track = True
        for goal in self.goals.all():
            on_track = on_track and goal.on_track
        return on_track

    @property
    def confirmation_url(self):
        return settings.SITE_URL + "/client/confirm/account/{0}".format(self.pk)

    def send_confirmation_email(self):

        subject = "BetaSmartz new account confirmation"

        context = {
            'advisor': self.primary_owner.advisor,
            'confirmation_url': self.confirmation_url,
            'account_type': self.get_account_class_display(),
        }

        send_mail(subject,
                  '',
                  None,
                  [self.primary_owner.user.email],
                  html_message=render_to_string('email/confirm_new_client_account.html', context))

    def __str__(self):
        return "{0}:{1}:{2}:({3})".format(
            self.primary_owner.full_name,
            self.primary_owner.advisor.first_name,
            self.primary_owner.advisor.firm.name, self.account_type_name)


FULL_TIME = "FULL_TIME"
PART_TIME = 'PART_TIME'
SELF_EMPLOYED = 'SELF_EMPLOYED'
STUDENT = "STUDENT"
RETIRED = "RETIRED"
HOMEMAKER = "HOMEMAKER"
UNEMPLOYED = "UNEMPLOYED"

EMPLOYMENT_STATUS_CHOICES = (
    (FULL_TIME, 'Employed (full-time)'), (PART_TIME, 'Employed (part-time)'),
    (SELF_EMPLOYED, 'Self-employed'), (STUDENT, 'Student'),
    (RETIRED, 'Retired'), (HOMEMAKER, 'Homemaker'),
    (UNEMPLOYED, "Not employed"))


class TaxFileNumberValidator(object):
    def __call__(self, value):

        if len(value) != 9:
            return False, 'Invalid TFN, check the digits.'

        weights = [1, 4, 3, 7, 5, 8, 6, 9, 10]
        _sum = 0

        try:
            for i in range(9):
                _sum += int(value[i]) * weights[i]
        except ValueError:
            return False, 'Invalid TFN, check the digits.'

        remainder = _sum % 11

        if remainder != 0:
            return False, 'Invalid TFN, check the digits.'

        return True, ""


class MedicareNumberValidator(object):
    def __call__(self, value):

        if len(value) != 11:
            return False, 'Invalid Medicare number.'

        weights = [1, 3, 7, 9, 1, 3, 7, 9]
        _sum = 0

        try:
            check_digit = int(value[8])
            for i in range(8):
                _sum += int(value[i]) * weights[i]
        except ValueError:
            return False, 'Invalid Medicare number.'

        remainder = _sum % 10

        if remainder != check_digit:
            return False, 'Invalid Medicare number.'

        return True, ""


class Client(NeedApprobation, NeedConfirmation, PersonalData):
    advisor = models.ForeignKey(Advisor, related_name="all_clients")
    secondary_advisors = models.ManyToManyField(
        Advisor,
        related_name='secondary_clients',
        editable=False)
    create_date = models.DateTimeField(auto_now_add=True)
    client_agreement = models.FileField()

    user = models.OneToOneField(User)
    tax_file_number = models.CharField(max_length=9, null=True, blank=True)
    provide_tfn = models.IntegerField(verbose_name="Provide TFN?",
                                      choices=TFN_CHOICES,
                                      default=TFN_YES)

    associated_to_broker_dealer = models.BooleanField(
        verbose_name="Are employed by or associated with "
                     "a broker dealer?",
        default=False,
        choices=YES_NO)
    ten_percent_insider = models.BooleanField(
        verbose_name="Are you a 10% shareholder, director, or"
                     " policy maker of a publicly traded company?",
        default=False,
        choices=YES_NO)

    public_position_insider = models.BooleanField(
        verbose_name="Do you or a family member hold a public office position?",
        default=False,
        choices=YES_NO)

    us_citizen = models.BooleanField(
        verbose_name="Are you a US citizen/person"
                     " for the purpose of US Federal Income Tax?",
        default=False,
        choices=YES_NO)

    employment_status = models.CharField(max_length=20,
                                         choices=EMPLOYMENT_STATUS_CHOICES)

    net_worth = models.FloatField(verbose_name="Net worth ($)", default=0)
    income = models.FloatField(verbose_name="Income ($)", default=0)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    employer = models.CharField(max_length=255, null=True, blank=True)
    betasmartz_agreement = models.BooleanField(default=False)
    advisor_agreement = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name()

    def rebuild_secondary_advisors(self):
        self.secondary_advisors.clear()
        # gell all the accounts
        for account in self.accounts.all():
            for secondary_advisor in account.account_group.secondary_advisors.all(
            ):
                self.secondary_advisors.add(secondary_advisor)

    @property
    def accounts(self):
        return self.accounts_all.filter(confirmed=True)

    @property
    def get_financial_plan(self):
        if hasattr(self, 'financial_plan'):
            plan = self.financial_plan
        else:
            return "null"
        betasmartz_externals = json.loads(serializers.serialize(
            "json", self.financial_plan_external_accounts.all()))
        external_accounts = []

        for be in betasmartz_externals:
            be["fields"]["id"] = be["pk"]
            external_accounts.append(be["fields"])

        betasmartz_goals = []

        for account in self.financial_plan_accounts.all():
            obj = dict()
            obj["id"] = account.pk
            obj["bettermentdb_account_id"] = account.account.pk
            obj["annual_contribution_cents"] = account.annual_contribution_cents
            betasmartz_goals.append(obj)

        plan = json.loads(serializers.serialize("json", [plan]))[0]
        plan["fields"]["id"] = plan["pk"]
        plan["fields"]["accounts"] = betasmartz_goals
        plan["fields"]["external_accounts"] = external_accounts
        plan["fields"]["income_replacement_ratio"] = plan["fields"][
            "income_replacement_ratio"]
        plan["fields"]["other_retirement_income_cents"] = plan["fields"][
            "other_retirement_income_cents"]
        plan["fields"]["desired_retirement_income_cents"] = plan["fields"][
            "desired_retirement_income_cents"]

        del plan["fields"]["client"]
        return mark_safe(json.dumps(plan["fields"]))

    @property
    def get_financial_profile(self):

        if hasattr(self, 'financial_profile'):
            profile = self.financial_profile
        else:
            return "null"

        data = json.loads(serializers.serialize("json", [profile]))[0]
        data["fields"]["id"] = data["pk"]
        del data["fields"]["client"]
        data["fields"]["social_security_percent_expected"] = str(data[
                                                                     "fields"]["social_security_percent_expected"])
        data["fields"]["annual_salary_percent_growth"] = str(data["fields"][
                                                                 "annual_salary_percent_growth"])
        data["fields"]["social_security_percent_expected"] = str(data[
                                                                     "fields"]["social_security_percent_expected"])
        data["fields"]["expected_inflation"] = str(data["fields"][
                                                       "expected_inflation"])

        return mark_safe(json.dumps(data["fields"]))

    @property
    def external_accounts(self):
        betasmartz_externals = json.loads(serializers.serialize(
            "json", self.financial_plan_external_accounts.all()))
        external_accounts = []

        for be in betasmartz_externals:
            be["fields"]["id"] = be["pk"]
            external_accounts.append(be["fields"])
        return mark_safe(json.dumps(external_accounts))

    @property
    def firm(self):
        return self.advisor.firm

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def age(self):
        born = self.date_of_birth
        today = date.today()
        return today.year - born.year - ((today.month, today.day) <
                                         (born.month, born.day))

    @property
    def total_balance(self):
        balance = 0
        for account in self.accounts.all():
            balance += account.total_balance
        return balance

    @property
    def stocks_percentage(self):
        return 0

    @property
    def bonds_percentage(self):
        return 0

    @property
    def total_returns(self):
        return 0

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        create_personal_account = False
        if self.pk is None:
            create_personal_account = True

        super(Client, self).save(force_insert, force_update, using,
                                 update_fields)

        if create_personal_account:
            new_ac = ClientAccount(primary_owner=self)
            new_ac.save()
            new_ac.remove_from_group()


BONDS = "BONDS"
STOCKS = "STOCKS"
MANAGED_FUNDS = "MANAGED_FUNDS"
INVESTMENT_TYPES = (("BONDS", "BONDS"), ("STOCKS", "STOCKS"), ("MANAGED_FUNDS", "MANAGED_FUNDS"))

SUPER_ASSET_CLASSES = (
    # EQUITY
    ("EQUITY_AU", "EQUITY_AU"),
    ("EQUITY_US", "EQUITY_US"),
    ("EQUITY_EU", "EQUITY_EU"),
    ("EQUITY_EM", "EQUITY_EM"),
    ("EQUITY_INT", "EQUITY_INT"),
    ("EQUITY_UK", "EQUITY_UK"),
    ("EQUITY_JAPAN", "EQUITY_JAPAN"),
    ("EQUITY_AS", "EQUITY_AS"),
    ("EQUITY_CN", "EQUITY_CN"),
    # FIXED_INCOME
    ("FIXED_INCOME_AU", "FIXED_INCOME_AU"),
    ("FIXED_INCOME_US", "FIXED_INCOME_US"),
    ("FIXED_INCOME_EU", "FIXED_INCOME_EU"),
    ("FIXED_INCOME_EM", "FIXED_INCOME_EM"),
    ("FIXED_INCOME_INT", "FIXED_INCOME_INT"),
    ("FIXED_INCOME_UK", "FIXED_INCOME_UK"),
    ("FIXED_INCOME_JAPAN", "FIXED_INCOME_JAPAN"),
    ("FIXED_INCOME_AS", "FIXED_INCOME_AS"),
    ("FIXED_INCOME_CN", "FIXED_INCOME_CN"),
    # Managed Funds
    ("MANAGED_FUNDS_AU", "MANAGED_FUNDS_AU"))


class AssetClass(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[0-9a-zA-Z_]+$',
            message="Invalid character only accept (0-9a-zA-Z_) ")])
    display_order = models.PositiveIntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True,
                                               default="",
                                               null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    investment_type = models.CharField(max_length=255,
                                       choices=INVESTMENT_TYPES,
                                       blank=False,
                                       null=False)
    super_asset_class = models.CharField(max_length=255,
                                         choices=SUPER_ASSET_CLASSES)

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        self.name = self.name.upper()

        super(AssetClass, self).save(force_insert, force_update, using,
                                     update_fields)

    @property
    def donut_order(self):
        return 8000 - self.display_order

    def __str__(self):
        return self.name


class Ticker(models.Model):
    symbol = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        validators=[RegexValidator(regex=r'^[^ ]+$',
                                   message="Invalid symbol format")])
    display_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    ordering = models.IntegerField(blank=True, default="", null=False)
    url = models.URLField()
    unit_price = models.FloatField(default=10)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")
    currency = models.CharField(max_length=10, default="AUD")

    def __str__(self):
        return self.symbol

    @property
    def primary(self):
        return "true" if self.ordering == 0 else "false"

    def shares(self, goal):
        return self.value(goal) / self.unit_price

    @property
    def is_stock(self):
        return self.asset_class.investment_type == STOCKS

    def value(self, goal):
        v = 0

        for p in Position.objects.filter(goal=goal, ticker=self).all():
            v += p.value

        return v

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        self.symbol = self.symbol.upper()

        super(Ticker, self).save(force_insert, force_update, using,
                                 update_fields)


class EmailInvitation(models.Model):
    email = models.EmailField()
    inviter_type = models.ForeignKey(ContentType)
    inviter_id = models.PositiveIntegerField()
    inviter_object = generic.GenericForeignKey('inviter_type', 'inviter_id')
    send_date = models.DateTimeField(auto_now=True)
    send_count = models.PositiveIntegerField(default=0)
    status = models.PositiveIntegerField(choices=EMAIL_INVITATION_STATUSES,
                                         default=INVITATION_PENDING)
    invitation_type = models.PositiveIntegerField(
        choices=INVITATION_TYPE_CHOICES,
        default=INVITATION_CLIENT)

    @property
    def get_status_name(self):
        for i in EMAIL_INVITATION_STATUSES:
            if self.status == i[0]:
                return i[1]

    @property
    def get_status(self):
        try:
            user = User.objects.get(email=self.email)
        except ObjectDoesNotExist:
            user = None

        if user.prepopulated:
            return INVITATION_PENDING

        if user is not None:
            if not user.is_active:
                self.status = INVITATION_CLOSED
                self.save()

            for it in INVITATION_TYPE_CHOICES:
                if self.invitation_type == it[0]:
                    model = INVITATION_TYPE_DICT[str(it[0])]
                    if hasattr(user, model):
                        # match advisor or firm
                        profile = getattr(user, model)
                        if (profile.firm == self.inviter_object) or \
                                (getattr(profile, 'advisor', None) == self.inviter_object):
                            if profile.is_confirmed:
                                self.status = INVITATION_ACTIVE
                                self.save()
                            else:
                                self.status = INVITATION_SUBMITTED
                                self.save()
        return self.status

    def send(self):

        if self.get_status != INVITATION_PENDING:
            return

        application_type = ""

        for itc in INVITATION_TYPE_CHOICES:
            if itc[0] == self.invitation_type:
                application_type = itc[1]

        subject = "BetaSmartz {application_type} sign up form url".format(
            application_type=application_type)
        inviter_type = self.inviter_object.get_inviter_type()
        inviter_name = self.inviter_object.get_inviter_name()
        invite_url = self.inviter_object.get_invite_url(self.invitation_type, self.email)

        context = {
            'subject': subject,
            'invite_url': invite_url,
            'inviter_name': inviter_type,
            'inviter_class': inviter_name,
            'application_type': application_type
        }

        send_mail(subject,
                  '',
                  None,
                  [self.email],
                  html_message=render_to_string('email/invite.html', context))
        self.send_count += 1

        self.save()


YAHOO_API = "YAHOO"
GOOGLE_API = "GOOGLE"
API_CHOICES = ((YAHOO_API, "YAHOO"), (GOOGLE_API, 'GOOGLE'))


class Platform(models.Model):
    fee = models.PositiveIntegerField(default=0)
    portfolio_set = models.ForeignKey('portfolios.PortfolioSet')
    api = models.CharField(max_length=20,
                           default=YAHOO_API,
                           choices=API_CHOICES)

    def __str__(self):
        return "BetaSmartz"


class Goal(models.Model):
    account = models.ForeignKey(ClientAccount, related_name="goals")
    name = models.CharField(max_length=100)
    target = models.FloatField(default=0)
    income = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField()
    allocation = models.FloatField() # The proportion of Stocks to use for the ETFs (Core Component) of the instrument mix for this goal
    satellite_pct = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], default=0.0, null=True) # The proportion of Managed Funds (Active component) to use in the instrument mix for this goal
    account_type = models.CharField(max_length=20, default='INVESTING')
    type = models.CharField(max_length=20, default='RETIREMENT')
    drift = models.FloatField(default=0)
    total_balance_db = models.FloatField(default=0,
                                         verbose_name="total balance")
    custom_portfolio_set = models.ForeignKey('portfolios.PortfolioSet', null=True, blank=True)
    custom_regions = models.TextField(null=True)
    custom_picked_regions = models.TextField(null=True)
    custom_optimization_mode = models.IntegerField(choices=[(0, 'None'), (1, 'auto mode'), (2, 'weight mode')], default=0)
    portfolios = models.TextField(null=True)
    custom_hedges = models.TextField(null=True)

    class Meta:
        ordering = ['name']

    @property
    def hedges(self):
        if self.custom_hedges is None:
            return mark_safe('null')
        else:
            return mark_safe(self.custom_hedges)

    @property
    def picked_regions(self):
        if self.custom_picked_regions is None:
            return mark_safe(self.portfolio_set.default_picked_regions)
        else:
            return mark_safe(self.custom_picked_regions)

    @property
    def optimization_mode(self):
        if self.custom_optimization_mode == 0:
            return self.portfolio_set.optimization_mode
        else:
            return self.custom_optimization_mode

    @property
    def regions_currencies(self):
        return mark_safe(json.dumps(self.portfolio_set.regions_currencies, sort_keys=True))

    @property
    def stocks_and_bonds(self):
        return self.portfolio_set.stocks_and_bonds

    @property
    def is_custom_size(self):
        if self.custom_regions is None:
            return False

        region_sizes = {}
        try:
            region_sizes = json.loads(self.custom_regions)
        except JSONDecodeError:
            pass

        if len(region_sizes) == 0:
            return False

        portfolio_set_regions = self.portfolio_set.regions

        total_size = 0
        for key in region_sizes.keys():
            if key not in portfolio_set_regions:
                self.custom_regions = None
                self.portfolios = None
                self.save()
                return False
            total_size += region_sizes[key]["size"]

        if total_size != 1:
            self.custom_regions = None
            self.portfolios = None
            self.save()
            return False

        return True

    @property
    def regions_allocation(self):
        if self.is_custom_size:
            return mark_safe(self.custom_regions)
        else:
            regions_allocation = {}
            sizes = json.loads(self.portfolio_set.default_region_sizes)
            for k in sizes:
                regions_allocation[k] = {"size": sizes[k]}
            return mark_safe(json.dumps(regions_allocation))

    @property
    def region_sizes(self):
        region_sizes = {}
        if self.is_custom_size:
            cr = json.loads(self.custom_regions)
            for k in cr:
                region_sizes[k] = cr[k]["size"]
            return region_sizes
        sizes = json.loads(self.portfolio_set.default_region_sizes)

        if len(sizes) == 0:
            raise Exception("bad region size for portfolio %s " % self.portfolio_set.name)
        return sizes

    def __str__(self):
        return self.name + " : " + self.account.primary_owner.full_name

    @property
    def get_financial_plan_id(self):
        try:
            FinancialPlanAccount.objects.get(account=self,
                                             client=self.account.primary_owner)
        except ObjectDoesNotExist:
            return "null"

        if hasattr(self.account.primary_owner, 'financial_plan'):
            return self.account.primary_owner.financial_plan.pk
        else:
            return "null"

    @property
    def get_financial_plan(self):
        try:
            FinancialPlanAccount.objects.get(account=self,
                                             client=self.account.primary_owner)
        except ObjectDoesNotExist:
            return "null"

        return self.account.primary_owner.get_financial_plan

    @property
    def portfolio_set(self):
        from portfolios.models import PortfolioSet

        if self.custom_portfolio_set is None:
            if "_ETHICAL" in self.type:
                if self.account.primary_owner.advisor.firm.can_use_ethical_portfolio:
                    self.custom_portfolio_set = PortfolioSet.objects.get(name="Ethical")
                    # TODO: be more smart about this
                    self.allocation = 1
                    self.save()
                    return self.custom_portfolio_set
            return Platform.objects.first().portfolio_set

        # check ethical portfolios
        if "_ETHICAL" in self.type:
            if not self.account.primary_owner.advisor.firm.can_use_ethical_portfolio:
                self.custom_portfolio_set = None
                self.save()
                return Platform.objects.first().portfolio_set
            else:
                # TODO: be more smart about this
                self.allocation = 1
                self.save()

        return self.custom_portfolio_set

    @property
    def target_portfolio(self):
        if self.is_custom_size:
            positions = json.loads(self.portfolios)
        else:
            positions = json.loads(self.portfolio_set.portfolios)
        return positions["{:.2f}".format(self.allocation)]

    @property
    def target_allocation(self):
        return self.target_portfolio["allocations"]

    @property
    def get_drift(self):
        tb = self.total_balance

        if tb == 0:
            return 0

        portfolio_set = self.portfolio_set
        tickers = Ticker.objects.filter(
            asset_class__in=portfolio_set.asset_classes.all())

        tickers_prices = []
        target_allocation = []
        current_allocation = []

        for ticker in tickers:
            tickers_prices.append(ticker.unit_price)
            target_allocation.append(self.target_allocation_dict.get(
                ticker.asset_class.name, 0))
            positions = Position.objects.filter(goal=self, ticker=ticker).all()
            cs = 0
            if positions:
                for p in positions:
                    cs += p.value
            current_allocation.append(cs / tb)

        current_allocation = array(current_allocation)
        target_allocation = array(target_allocation)

        return float("{0:.2f}".format(sum(abs(
            current_allocation - target_allocation)) / (3 / 2) / 2 * 100))

    @property
    def life_time_average_balance(self):
        return 0

    @property
    def life_time_personal_return(self):
        return 0

    @property
    def total_earned(self):
        return 0

    @property
    def portfolio_set_id(self):
        return self.portfolio_set.pk

    @property
    def available_balance(self):
        return self.total_balance + self.pending_withdrawals

    @property
    def pending_deposits(self):
        pd = 0.0
        for d in Transaction.objects.filter(account=self,
                                            status=PENDING,
                                            type=DEPOSIT).all():
            pd += d.amount
        return pd

    @property
    def pending_withdrawals(self):
        pw = 0.0
        for w in Transaction.objects.filter(account=self,
                                            status=PENDING,
                                            type=WITHDRAWAL).all():
            pw -= w.amount
        return pw

    @property
    def total_deposits(self):
        pd = 0.0
        for d in Transaction.objects.filter(account=self,
                                            status=EXECUTED,
                                            type=DEPOSIT).all():
            pd += d.amount
        return pd

    @property
    def total_withdrawals(self):
        pw = 0.0
        for w in Transaction.objects.filter(account=self,
                                            status=EXECUTED,
                                            type=WITHDRAWAL).all():
            pw -= w.amount
        return pw

    @property
    def total_dividends(self):
        return 0.0

    @property
    def market_changes(self):
        return 0.0

    @property
    def total_invested(self):
        return self.total_deposits

    @property
    def life_time_return(self):
        return 0.0

    @property
    def other_adjustments(self):
        return 0.0

    @property
    def pending_conversions(self):
        return 0

    @property
    def cash_balance(self):
        return 0.0

    @property
    def total_fees(self):
        return 0.0

    @property
    def recharacterized(self):
        return 0

    @property
    def on_track(self):
        current_balance = self.total_balance + self.pending_deposits - self.pending_withdrawals
        today = date.today()
        term = self.completion_date.year - today.year
        expected_return = self.target_portfolio["expectedReturn"] / 100 + self.portfolio_set.risk_free_rate
        expected_value = current_balance * (1 + expected_return) ** term
        if hasattr(self, "auto_deposit"):
            ada = self.auto_deposit.get_annualized
            for i in range(0, term):
                expected_value += ada * (1 + expected_return) ** (term - i)
        if hasattr(self, "auto_withdrawal"):
            ada = self.auto_withdrawal.get_annualized
            for i in range(0, term):
                expected_value -= ada * (1 + expected_return) ** (term - i)
        return expected_value >= self.target

    @property
    def total_balance(self):
        b = 0
        for p in Position.objects.filter(goal=self).all():
            b += p.value
        return b

    @property
    def stock_balance(self):
        v = 0
        for p in self.positions.all():
            if p.is_stock:
                v += p.value
        return v

    @property
    def bond_balance(self):
        v = 0
        for p in self.positions.all():
            if not p.is_stock:
                v += p.value
        return v

    @property
    def total_return(self):
        return 0

    @property
    def stocks_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.stock_balance / self.total_balance * 100)))

    @property
    def bonds_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.bond_balance / self.total_balance * 100)))

    @property
    def auto_frequency(self):
        if not hasattr(self, "auto_deposit"):
            return "-"
        return self.auto_deposit.get_frequency_display()

    @property
    def auto_amount(self):
        if not hasattr(self, "auto_deposit"):
            return "-"
        return self.auto_deposit.amount

    @property
    def auto_term(self):
        today = date.today()
        return "{0}y".format(self.completion_date.year - today.year)


class Position(models.Model):
    goal = models.ForeignKey(Goal, related_name='positions')
    ticker = models.ForeignKey(Ticker)
    share = models.FloatField()

    @property
    def is_stock(self):
        return self.ticker.is_stock

    @property
    def value(self):
        return self.share * self.ticker.unit_price

    def __str__(self):
        return self.ticker.symbol


class Transaction(models.Model):
    account = models.ForeignKey(Goal, related_name="transactions")
    type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    from_account = models.ForeignKey(ClientAccount,
                                     related_name="transactions_from",
                                     null=True,
                                     blank=True)
    to_account = models.ForeignKey(ClientAccount,
                                   related_name="transactions_to",
                                   null=True,
                                   blank=True)
    amount = models.FloatField(default=0)
    status = models.CharField(max_length=20,
                              choices=TRANSACTION_STATUS_CHOICES,
                              default=PENDING)
    created_date = models.DateTimeField(auto_now_add=True)
    executed_date = models.DateTimeField(null=True)
    new_balance = models.FloatField(default=0)
    inversion = models.FloatField(default=0)
    return_fraction = models.FloatField(default=0)


class DataApiDict(models.Model):
    api = models.CharField(choices=API_CHOICES, max_length=50)
    platform_symbol = models.CharField(max_length=20)
    api_symbol = models.CharField(max_length=20)


class TransactionMemo(models.Model):
    category = models.CharField(max_length=255)
    comment = models.TextField()
    transaction_type = models.CharField(max_length=20)
    transaction = models.ForeignKey(Transaction, related_name="memos")


MONTHLY = "MONTHLY"
TWICE_A_MONTH = "TWICE_A_MONTH"
EVERY_OTHER_WEEK = "EVERY_OTHER_WEEK"
WEEKLY = "WEEKLY"

FREQUENCY_CHOICES = ((MONTHLY, "1/mo"), (TWICE_A_MONTH, "2/mo"),
                     (EVERY_OTHER_WEEK, "2/mo"), (WEEKLY, 'WEEKLY'))


class AutomaticWithdrawal(models.Model):
    account = models.OneToOneField(Goal, related_name="auto_withdrawal")
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    enabled = models.BooleanField(default=True)
    amount = models.FloatField()
    transaction_date_time_1 = models.DateTimeField(null=True)
    transaction_date_time_2 = models.DateTimeField(null=True)
    last_plan_change = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_transaction(self):
        return date.today()

    @property
    def is_enabled(self):
        return "true" if self.enabled else "false"

    @property
    def get_annualized(self):

        if self.frequency == MONTHLY:
            return self.amount * 12
        elif self.frequency == TWICE_A_MONTH:
            return self.amount * 2 * 12
        elif self.frequency == EVERY_OTHER_WEEK:
            return self.amount * 2 * 12
        elif self.frequency == WEEKLY:
            return self.amount * 4 * 12

        return 0


class AutomaticDeposit(models.Model):
    account = models.OneToOneField(Goal, related_name="auto_deposit")
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    enabled = models.BooleanField(default=True)
    amount = models.FloatField()
    transaction_date_time_1 = models.DateTimeField(null=True)
    transaction_date_time_2 = models.DateTimeField(null=True)
    last_plan_change = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_transaction(self):
        return date.today()

    @property
    def is_enabled(self):
        return "true" if self.enabled else "false"

    @property
    def get_annualized(self):

        if self.frequency == MONTHLY:
            return self.amount * 12
        elif self.frequency == TWICE_A_MONTH:
            return self.amount * 2 * 12
        elif self.frequency == EVERY_OTHER_WEEK:
            return self.amount * 2 * 12
        elif self.frequency == WEEKLY:
            return self.amount * 4 * 12

        return 0


class SymbolReturnHistory(models.Model):
    return_number = models.FloatField(default=0)
    symbol = models.CharField(max_length=20)
    date = models.DateField()


STRATEGY = "STRATEGY"
BENCHMARK = "BENCHMARK"
BOND = "BOND"
STOCK = "STOCK"
PERFORMER_GROUP_CHOICE = ((STRATEGY, "STRATEGY"), (BENCHMARK, "BENCHMARK"),
                          (BOND, "BOND"), (STOCK, "STOCK"))


class Performer(models.Model):
    symbol = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=20,
                             choices=PERFORMER_GROUP_CHOICE,
                             default=BENCHMARK)
    allocation = models.FloatField(default=0)
    portfolio_set = models.ForeignKey('portfolios.PortfolioSet')


class CostOfLivingIndex(models.Model):
    state = AUStateField(unique=True)
    value = models.FloatField(default=80.99)


class FinancialPlanAccount(models.Model):
    client = models.ForeignKey(Client, related_name="financial_plan_accounts")
    account = models.ForeignKey(Goal)
    annual_contribution_cents = models.CharField(max_length=100, null=True)


class FinancialPlanExternalAccount(models.Model):
    client = models.ForeignKey(Client,
                               related_name="financial_plan_external_accounts")
    account_type = models.CharField(max_length=100)
    balance_cents = models.FloatField(default=0, null=True)
    annual_contribution_cents = models.FloatField(default=0, null=True)
    account_owner = models.CharField(max_length=100, null=True)
    institution_name = models.CharField(max_length=255, null=True)
    investment_type = models.CharField(max_length=100, null=True)
    advisor_fee_percent = models.CharField(max_length=100, null=True)


class FinancialPlan(models.Model):
    client = models.OneToOneField(Client, related_name="financial_plan")
    name = models.CharField(max_length=100)
    other_retirement_income_cents = models.FloatField(default=0)
    complete = models.BooleanField(default=False)
    retirement_zip = AUPostCodeField()
    income_replacement_ratio = models.FloatField(null=True)
    retirement_age = models.PositiveIntegerField(null=True)
    spouse_retirement_age = models.PositiveIntegerField(null=True)
    desired_retirement_income_cents = models.FloatField(default=0)
    savings_advice_chance = models.CharField(max_length=100, null=True)


class FinancialProfile(models.Model):
    client = models.OneToOneField(Client, related_name="financial_profile")
    complete = models.BooleanField(default=False)
    marital_status = models.CharField(default="single", max_length=100)
    retired = models.BooleanField(default=False)
    life_expectancy = models.FloatField(default=70, null=True)
    pretax_income_cents = models.FloatField(default=0, null=True)
    social_security_monthly_amount_cents = models.FloatField(default=0,
                                                             null=True)
    expected_inflation = models.FloatField(default=2.5)
    social_security_percent_expected = models.FloatField(default=0, null=True)
    annual_salary_percent_growth = models.FloatField(default=0, null=True)
    average_tax_percent = models.FloatField(default=0, null=True)
    spouse_name = models.CharField(max_length=100, null=True)
    spouse_estimated_birthdate = models.DateTimeField(null=True)
    spouse_retired = models.BooleanField(default=False)
    spouse_life_expectancy = models.FloatField(default=80, null=True)
    spouse_pretax_income_cents = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MonthlyPrices(models.Model):
    symbol = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    date = models.DateField()

    class Meta:
        ordering = ["symbol", "date"]