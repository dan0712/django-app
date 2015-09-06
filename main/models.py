from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, _,\
    validators, UserManager, timezone,\
    send_mail
from django.core.validators import RegexValidator, ValidationError
from .fields import ColorField
from django_localflavor_au.models import AUPhoneNumberField, AUStateField, AUPostCodeField
from main.slug import unique_slugify
from django.conf import settings
import uuid
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django import forms
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
from datetime import date

def validate_agreement(value):
    if value is False:
        raise ValidationError("You must accept the agreement to continue.")

SUCCESS_MESSAGE = "Your application has been submitted successfully, you will receive a confirmation email" \
                  " following a BetaSmartz approval."

INVITATION_PENDING = 0
INVITATION_SUBMITTED = 1
INVITATION_ACTIVE = 3
INVITATION_CLOSED = 4

EMAIL_INVITATION_STATUSES = ((INVITATION_PENDING, 'Pending'),
                             (INVITATION_SUBMITTED, 'Submitted'),
                             (INVITATION_ACTIVE, 'Active'),
                             (INVITATION_CLOSED, 'Closed'))


INVITATION_ADVISOR = 0
AUTHORIZED_REPRESENTATIVE = 1
INVITATION_SUPERVISOR = 2
INVITATION_CLIENT = 3
INVITATION_TYPE_CHOICES = ((INVITATION_ADVISOR, "Advisor"),
                           (AUTHORIZED_REPRESENTATIVE, 'Authorised representative'),
                           (INVITATION_CLIENT, 'Client'),
                           (INVITATION_SUPERVISOR, 'Supervisor'))

INVITATION_TYPE_DICT = {str(INVITATION_ADVISOR): "advisor",
                        str(AUTHORIZED_REPRESENTATIVE): "authorised_representative",
                        str(INVITATION_CLIENT): "client",
                        str(INVITATION_SUPERVISOR): "supervisor"}


TFN_YES = 0
TFN_NON_RESIDENT = 1
TFN_CLAIM = 2
TFN_DONT_WANT = 3

TFN_CHOICES = ((TFN_YES, "Yes"),
               (TFN_NON_RESIDENT, "I am a non-resident of Australia"),
               (TFN_CLAIM, "I want to claim an exemption"),
               (TFN_DONT_WANT, "I do not want to quote a Tax File Number or exemption"),)

Q1 = "What was the name of your elementary school?"
Q2 = "What was the name of your favorite childhood friend?"
Q3 = "What was the name of your childhood pet?"
Q4 = "What street did you live on in third grade?"
Q5 = "What is your oldest sibling's birth month?"
Q6 = "In what city did your mother and father meet?"

QUESTION_1_CHOICES = ((Q1, Q1),
                      (Q2, Q2),
                      (Q3, Q3))

QUESTION_2_CHOICES = ((Q4, Q4),
                      (Q5, Q5),
                      (Q6, Q6))


PERSONAL_DATA_FIELDS = ('date_of_birth', 'gender', 'address_line_1', 'address_line_2', 'city', 'state',
                        'post_code', 'phone_number', 'security_question_1', "security_question_2",
                        "security_answer_1", "security_answer_2", 'medicare_number')


PERSONAL_DATA_WIDGETS = {"gender": forms.RadioSelect(),
                         "date_of_birth": forms.TextInput(attrs={"placeholder": "YYYY-MM-DD"}),
                         'address_line_1': forms.TextInput(attrs={"placeholder": "Street address"}),
                         "address_line_2": forms.TextInput(
                             attrs={"placeholder": "Apartment, Suite, Unit, Floor (optional)"})}


class BetaSmartzAgreementForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(BetaSmartzAgreementForm, self).clean()
        if not(cleaned_data["betasmartz_agreement"] is True):
            self._errors['betasmartz_agreement'] = mark_safe('<ul class="errorlist">'
                                                             '<li>You must accept the BetaSmartz\'s agreement'
                                                             ' to continue.</li></ul>')

        return cleaned_data


class BetaSmartzGenericUSerSignupForm(BetaSmartzAgreementForm):

    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    user_profile_type = None

    def clean(self):
        cleaned_data = super(BetaSmartzGenericUSerSignupForm, self).clean()
        self._validate_unique = False

        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')

        if password1 and (password1 != password2):
            self._errors['confirm_password'] = mark_safe('<ul class="errorlist"><li>Passwords don\'t match.</li></ul>')

        # check if user already exist
        try:
            user = User.objects.get(email=cleaned_data.get('email'))
        except ObjectDoesNotExist:
            user = None

        if user is not None:
            # confirm password
            if not user.check_password(password1):
                    self._errors['email'] = mark_safe(u'<ul class="errorlist"><li>User already exists</li></ul>')
            else:
                if hasattr(user, self.user_profile_type):
                    rupt = self.user_profile_type.replace("_", " ")
                    self._errors['email'] = mark_safe(u'<ul class="errorlist"><li>User already has an'
                                                      u' {0} account</li></ul>'.format(rupt))

        cleaned_data["password"] = make_password(password1)
        return cleaned_data

    def save(self, *args, **kw):
        # check if user already exist
        try:
            self.instance = User.objects.get(email=self.cleaned_data.get('email'))
        except ObjectDoesNotExist:
            pass
        return super(BetaSmartzGenericUSerSignupForm, self).save(*args, **kw)


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
        pass

    def send_approve_email(self):
        account_type = self._meta.verbose_name

        subject = "Your BetaSmartz new {0} account have been approved".format(account_type)

        context = {'subject': subject,
                   'account_type': account_type,
                   'firm_name': self.firm.name}

        send_mail(subject, '', None, [self.email], html_message=render_to_string('email/approve_account.html', context))


class NeedConfirmation(models.Model):

    class Meta:
        abstract = True

    confirmation_key = models.CharField(max_length=36, null=True, blank=True, editable=False)
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

        return settings.SITE_URL + "/confirm_email/{0}/{1}".format(self.content_type, self.confirmation_key)

    def send_confirmation_email(self):
        account_type = self._meta.verbose_name

        subject = "BetaSmartz new {0} account confirmation".format(account_type)

        context = {'subject': subject,
                   'account_type': account_type,
                   'confirmation_url': self.get_confirmation_url(),
                   'firm_name': self.firm.name}

        send_mail(subject, '', None, [self.email], html_message=render_to_string('email/confirmation.html', context))


class PersonalData(models.Model):
    class Meta:
        abstract = True

    date_of_birth = models.DateField(verbose_name="Date of birth")
    gender = models.CharField(max_length=20, default="Male",  choices=(("Male", "Male"), ("Female", "Female")))
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = AUStateField()
    post_code = AUPostCodeField()
    phone_number = AUPhoneNumberField()
    security_question_1 = models.CharField(max_length=255, choices=QUESTION_1_CHOICES)
    security_question_2 = models.CharField(max_length=255, choices=QUESTION_2_CHOICES)
    security_answer_1 = models.CharField(max_length=255, verbose_name="Answer")
    security_answer_2 = models.CharField(max_length=255, verbose_name="Answer")
    medicare_number = models.CharField(max_length=50)

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
        return self.work_phone[0:4] + "-" + self.work_phone[4:7] + "-" + self.work_phone[7:10]

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
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30)
    username = models.CharField(max_length=30, editable=False, default='')
    email = models.EmailField(_('email address'), unique=True,
                              error_messages={
                                  'unique': _("A user with that email already exists."),
                                  })

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

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
    dealer_group_number = models.CharField(max_length=50, null=True, blank=True)
    slug = models.CharField(max_length=100, editable=False, unique=True)
    logo_url = models.ImageField(verbose_name="White logo", null=True, blank=True)
    knocked_out_logo_url = models.ImageField(verbose_name="Colored logo", null=True, blank=True)
    client_agreement_url = models.FileField(verbose_name="Client Agreement (PDF)", null=True, blank=True)
    form_adv_part2_url = models.FileField(verbose_name="Form Adv", null=True, blank=True)
    token = models.CharField(max_length=36, editable=False)
    fee = models.PositiveIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

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

        super(Firm, self).save(force_insert, force_update, using, update_fields)

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

    def get_invite_url(self, application_type):
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
    office_address_line_1 = models.CharField("Office address 1", max_length=255)
    office_address_line_2 = models.CharField("Office address 2", max_length=255, null=True, blank=True)
    office_state = AUStateField()
    office_city = models.CharField(max_length=255)
    office_post_code = AUPostCodeField()
    postal_address_line_1 = models.CharField("Postal address 1", max_length=255)
    postal_address_line_2 = models.CharField("Postal address 2", max_length=255, null=True, blank=True)
    postal_state = AUStateField()
    same_address = models.BooleanField(default=False)
    postal_city = models.CharField(max_length=255)
    postal_post_code = AUPostCodeField()
    daytime_phone_number = AUPhoneNumberField()
    mobile_phone_number = AUPhoneNumberField()
    fax_number = AUPhoneNumberField()
    alternate_email_address = models.EmailField("Email address", null=True, blank=True)
    last_change = models.DateField(auto_now=True)
    fee_bank_account_name = models.CharField('Name', max_length=100)
    fee_bank_account_branch_name = models.CharField('Branch name', max_length=100)
    fee_bank_account_bsb_number = models.CharField('BSB number', max_length=20)
    fee_bank_account_number = models.CharField('Account number', max_length=20)
    fee_bank_account_holder_name = models.CharField('Account holder', max_length=100)
    australian_business_number = models.CharField("ABN", max_length=20)


class Advisor(NeedApprobation, NeedConfirmation, PersonalData):
    user = models.OneToOneField(User, related_name="advisor")
    token = models.CharField(max_length=36, null=True, editable=False)
    firm = models.ForeignKey(Firm, related_name="advisors")
    letter_of_authority = models.FileField()
    betasmartz_agreement = models.BooleanField()

    @property
    def firm_colored_logo(self):
        return self.firm.knocked_out_logo_url

    def get_invite_url(self, *args, **kwargs):
        if self.token is None:
            return ''
        return settings.SITE_URL + "/" + self.firm.slug + "/client/signup/" + self.token

    @staticmethod
    def get_inviter_type():
        return "advisor"

    @property
    def total_balance(self):
        return 0

    @property
    def total_account_groups(self):
        return self.secondary_account_groups.count() + self.primary_account_groups.count()

    @property
    def average_balance(self):
        if self.total_account_groups>0:
            return self.total_balance / self.total_account_groups
        return 0

    def get_inviter_name(self):
        return self.user.get_full_name()

    def save(self, *args, **kw):
        send_confirmation_mail = False
        if self.pk is not None:
            orig = Advisor.objects.get(pk=self.pk)
            if (orig.is_accepted != self.is_accepted) and (self.is_accepted is True):
                send_confirmation_mail = True

        super(Advisor, self).save(*args, **kw)
        if send_confirmation_mail and (self.confirmation_key is not None):
            self.user.email_user("BetaSmartz advisor account confirmation",
                                 "You advisor account have been approved, "
                                 "please confirm your email here: "
                                 "{site_url}/advisor/confirm_email/{confirmation_key}/"
                                 " \n\n\n  The BetaSmartz Team"
                                 .format(confirmation_key=self.confirmation_key,
                                         site_url=settings.SITE_URL))


class AuthorisedRepresentative(NeedApprobation, NeedConfirmation, PersonalData):
    user = models.OneToOneField(User, related_name='authorised_representative')
    firm = models.ForeignKey(Firm, related_name='authorised_representatives')
    letter_of_authority = models.FileField()
    betasmartz_agreement = models.BooleanField()


class AccountGroup(models.Model):
    advisor = models.ForeignKey(Advisor, related_name="primary_account_groups")
    secondary_advisors = models.ManyToManyField(Advisor, related_name='secondary_account_groups')
    name = models.CharField(max_length=100)

    @property
    def total_balance(self):
        return 0

    @property
    def total_returns(self):
        return 0

    @property
    def allocation(self):
        return 0

    @property
    def stocks_percentage(self):
        return self.allocation * 100.0

    @property
    def bonds_percentage(self):
        return (1-self.allocation) * 100.0

    @property
    def on_track(self):
        return False

    @property
    def since(self):
        min_created_at = self.accounts.first().created_at

        for account in self.accounts.all():
            if min_created_at > account.created_at:
                min_created_at = account.created_at

        return min_created_at

    def __str__(self):
        return self.name


PERSONAL_ACCOUNT = 1

ACCOUNT_TYPES = ((PERSONAL_ACCOUNT, "Personal Account"), )


class ClientAccount(models.Model):
    account_group = models.ForeignKey(AccountGroup, related_name="accounts", null=True)
    custom_fee = models.PositiveIntegerField(default=0)
    account_type = models.PositiveIntegerField(choices=ACCOUNT_TYPES, default=PERSONAL_ACCOUNT)
    primary_owner = models.ForeignKey('Client', related_name="accounts")
    created_at = models.DateTimeField(auto_now_add=True)

    def remove_from_group(self):
        old_group = self.account_group

        # get personal group or create it
        group_name = "{0}".format(self.primary_owner.full_name)
        groups = AccountGroup.objects.filter(name=group_name, advisor=self.primary_owner.advisor)
        if groups:
            group = groups[0]
        else:
            group = AccountGroup(name=group_name, advisor=self.primary_owner.advisor)
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
            return self.primary_owner.advisor.firm.fee + Platform.objects.first().fee

    @property
    def total_balance(self):
        return 0

    @property
    def total_returns(self):
        return 0

    @property
    def stocks_percentage(self):
        return 0

    @property
    def bonds_percentage(self):
        return 0

    @property
    def owners(self):
        return self.primary_owner.full_name

    @property
    def account_type_name(self):
        for at in ACCOUNT_TYPES:
            if at[0] == self.account_type:
                return at[1]

    @property
    def on_track(self):
        return False

    def __str__(self):
        return "{0}:{1}:{2}:({3})".format(self.primary_owner.full_name,
                                          self.primary_owner.advisor.first_name,
                                          self.primary_owner.advisor.firm.name,
                                          self.account_type_name)


class Client(NeedApprobation, NeedConfirmation):
    advisor = models.ForeignKey(Advisor, related_name="clients")
    secondary_advisors = models.ManyToManyField(Advisor, related_name='secondary_clients', editable=False)
    create_date = models.DateTimeField(auto_now_add=True)
    client_agreement = models.FileField()

    user = models.OneToOneField(User)
    date_of_birth = models.DateField(verbose_name="Date of birth")
    gender = models.CharField(max_length=20, default="Male",  choices=(("Male", "Male"), ("Female", "Female")))
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = AUStateField()
    post_code = AUPostCodeField()
    phone_number = AUPhoneNumberField()
    tax_file_number = models.CharField(max_length=50)
    provide_tfn = models.IntegerField(verbose_name="Provide TFN?", choices=TFN_CHOICES, default=TFN_YES)
    security_question_1 = models.CharField(max_length=255, choices=QUESTION_1_CHOICES)
    security_question_2 = models.CharField(max_length=255, choices=QUESTION_2_CHOICES)
    security_answer_1 = models.CharField(max_length=255, verbose_name="Answer")
    security_answer_2 = models.CharField(max_length=255, verbose_name="Answer")
    associated_to_broker_dealer = models.BooleanField(verbose_name="You are employed by or associated with "
                                                                   "a broker dealer.",
                                                      default=False,
                                                      choices=YES_NO)
    ten_percent_insider = models.BooleanField(verbose_name="You are a 10% shareholder, director, or"
                                                           " policy maker of a publicly traded company.",
                                              default=False,
                                              choices=YES_NO)

    def __str__(self):
        return self.user.get_full_name()

    def rebuild_secondary_advisors(self):
        self.secondary_advisors.clear()
        # gell all the accounts
        for account in self.accounts.all():
            for secondary_advisor in account.account_group.secondary_advisors.all():
                self.secondary_advisors.add(secondary_advisor)
        pass

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
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        create_personal_account = False
        if self.pk is None:
            create_personal_account = True

        super(Client, self).save(force_insert, force_update, using, update_fields)

        if create_personal_account:
            new_ac = ClientAccount(primary_owner=self)
            new_ac.save()


INVESTMENT_TYPES = (("BONDS", "BONDS"), ("STOCKS", "STOCKS"))


SUPER_ASSET_CLASSES = (
    # EQUITY
    ("EQUITY_AU", "EQUITY_AU"), ("EQUITY_US", "EQUITY_US"), ("EQUITY_EU", "EQUITY_EU"), ("EQUITY_EM", "EQUITY_EM"),
    ("EQUITY_INT", "EQUITY_INT"),
    # FIXED_INCOME
    ("FIXED_INCOME_AU", "FIXED_INCOME_AU"), ("FIXED_INCOME_US", "FIXED_INCOME_US"),
    ("FIXED_INCOME_EU", "FIXED_INCOME_EU"), ("FIXED_INCOME_EM", "FIXED_INCOME_EM"),
    ("FIXED_INCOME_INT", "FIXED_INCOME_INT")

)


class AssetClass(models.Model):
    name = models.CharField(max_length=255, validators=[RegexValidator(regex=r'^[0-9a-zA-Z_]+$',
                                                        message="Invalid character only accept (0-9a-zA-Z_) ")])
    display_order = models.PositiveIntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True, default="", null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    investment_type = models.CharField(max_length=255, choices=INVESTMENT_TYPES,  blank=False, null=False)
    super_asset_class = models.CharField(max_length=255, choices=SUPER_ASSET_CLASSES)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.name = self.name.upper()

        super(AssetClass, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, blank=False, null=False, validators=[RegexValidator(regex=r'^[^ ]+$',
                                                                                  message="Invalid symbol format")])
    display_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    ordering = models.IntegerField(blank=True, default="", null=False)
    url = models.URLField()
    unit_price = models.FloatField(default=1, editable=False)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")

    def __str__(self):
        return self.symbol

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.symbol = self.symbol.upper()

        super(Ticker, self).save(force_insert, force_update, using, update_fields)


class EmailInvitation(models.Model):

    email = models.EmailField()
    inviter_type = models.ForeignKey(ContentType)
    inviter_id = models.PositiveIntegerField()
    inviter_object = generic.GenericForeignKey('inviter_type', 'inviter_id')
    send_date = models.DateTimeField(auto_now=True)
    send_count = models.PositiveIntegerField(default=0)
    status = models.PositiveIntegerField(choices=EMAIL_INVITATION_STATUSES, default=INVITATION_PENDING)
    invitation_type = models.PositiveIntegerField(choices=INVITATION_TYPE_CHOICES, default=INVITATION_CLIENT)

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

        subject = "BetaSmartz {application_type} sign up form url".format(application_type=application_type)
        inviter_type = self.inviter_object.get_inviter_type()
        inviter_name = self.inviter_object.get_inviter_name()
        invite_url = self.inviter_object.get_invite_url(self.invitation_type)

        context = {'subject': subject,
                   'invite_url': invite_url,
                   'inviter_name': inviter_type,
                   'inviter_class': inviter_name,
                   'application_type': application_type}

        send_mail(subject, '', None, [self.email],
                  html_message=render_to_string('email/invite.html', context))
        self.send_count += 1

        self.save()


class Platform(models.Model):
    fee = models.PositiveIntegerField(default=0)


class Goal(models.Model):
    account = models.ForeignKey(ClientAccount, related_name="goals")
    name = models.CharField(max_length=100)
    target = models.FloatField(default=0)

    @property
    def on_track(self):
        return False

    @property
    def total_balance(self):
        return 0

    @property
    def total_return(self):
        return 0

    @property
    def stocks_percentage(self):
        return 0

    @property
    def bonds_percentage(self):
        return 0

    @property
    def auto_frequency(self):
        return "-"

    @property
    def auto_amount(self):
        return "-"

    @property
    def auto_term(self):
        return "-"
