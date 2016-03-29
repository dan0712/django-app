import datetime
import importlib
import json
import logging
import uuid
from datetime import date
from enum import Enum, unique
from itertools import chain, zip_longest, repeat

import scipy.stats as st

from django import forms
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, _,
    UserManager, timezone,
    send_mail
)
from django.core import serializers
from django.core.validators import (
    RegexValidator, ValidationError, MinValueValidator,
    MaxValueValidator, MinLengthValidator
)
from django.db import models, transaction
from django.db.models.deletion import PROTECT, CASCADE
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_localflavor_au.models import AUPhoneNumberField, AUStateField, AUPostCodeField
from recurrence.base import deserialize
from rest_framework.authtoken.models import Token
from django_pandas.managers import DataFrameManager

from main.management.commands.build_returns import get_price_returns
from main.slug import unique_slugify
from .fields import ColorField
from .managers import (
    ClientAccountQuerySet, GoalQuerySet,
)

logger = logging.getLogger('main.models')


def validate_agreement(value):
    if value is False:
        raise ValidationError("You must accept the agreement to continue.")


def validate_module(value):
    if not value.strip():
        raise ValidationError("The supplied module: {} cannot be blank.".format(value))
    module_spec = importlib.util.find_spec(value)
    if module_spec is None:
        raise ValidationError("The supplied module: {} could not be found.".format(value))


@unique
class ChoiceEnum(Enum):
    """
    ChoiceEnum is used when you want to use an enumeration for the choices of an integer django field.
    """
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


@unique
class StandardAssetFeatures(Enum):
    SRI = 0
    ASSET_TYPE = 1
    FUND_TYPE = 2
    REGION = 3

    def get_object(self):
        names = {
            # feature_tag: feature_name
            self.SRI: 'Social Responsibility',
            self.ASSET_TYPE: 'Asset Type',
            self.FUND_TYPE: 'Fund Type',
            self.REGION: 'Region',
            # TODO: Add the rest
        }
        return AssetFeature.objects.get_or_create(name=names[self.value])[0]


@unique
class StandardAssetFeatureValues(Enum):
    SRI_OTHER = 0
    ASSET_TYPE_STOCK = 1
    ASSET_TYPE_BOND = 2
    FUND_TYPE_CORE = 3
    FUND_TYPE_SATELLITE = 4
    REGION_AUSTRALIAN = 5
    # TODO: Add the rest

    def get_object(self):
        data = {
            # feature_value_tag: (feature_tag, feature_value_name)
            self.SRI_OTHER: (StandardAssetFeatures.SRI, 'Non-specific Social Responsibility Initiative'),
            self.ASSET_TYPE_STOCK: (StandardAssetFeatures.ASSET_TYPE, 'Stocks only'),
            self.ASSET_TYPE_BOND: (StandardAssetFeatures.ASSET_TYPE, 'Bonds only'),
            self.FUND_TYPE_CORE: (StandardAssetFeatures.FUND_TYPE, 'Core'),
            self.FUND_TYPE_SATELLITE: (StandardAssetFeatures.FUND_TYPE, 'Satellite'),
            self.REGION_AUSTRALIAN: (StandardAssetFeatures.REGION, 'Australian'),
        }
        return AssetFeatureValue.objects.get_or_create(name=data[self.value][1],
                                                       defaults={'feature': data[self.value][0].get_object()})[0]


SUCCESS_MESSAGE = "Your application has been submitted successfully, you will receive a confirmation email" \
                  " following a BetaSmartz approval."

INVITATION_PENDING = 0
INVITATION_SUBMITTED = 1
INVITATION_ACTIVE = 3
INVITATION_CLOSED = 4

EMAIL_INVITATION_STATUSES = (
    (INVITATION_PENDING, 'Pending'), (INVITATION_SUBMITTED, 'Submitted'),
    (INVITATION_ACTIVE, 'Active'), (INVITATION_CLOSED, 'Closed'))

EMPLOYMENT_STATUS_FULL_TIME = 0
EMPLOYMENT_STATUS_PART_TIME = 1
EMPLOYMENT_STATUS_SELF_EMPLOYED = 1
EMPLOYMENT_STATUS_STUDENT = 2
EMPLOYMENT_STATUS_RETIRED = 3
EMPLOYMENT_STATUS_HOMEMAKER = 4
EMPLOYMENT_STATUS_UNEMPLOYED = 5
EMPLOYMENT_STATUSES = (
    (EMPLOYMENT_STATUS_FULL_TIME, 'Employed (full-time)'),
    (EMPLOYMENT_STATUS_PART_TIME, 'Employed (part-time)'),
    (EMPLOYMENT_STATUS_SELF_EMPLOYED, 'Self-employed'),
    (EMPLOYMENT_STATUS_STUDENT, 'Student'),
    (EMPLOYMENT_STATUS_RETIRED, 'Retired'),
    (EMPLOYMENT_STATUS_HOMEMAKER, 'Homemaker'),
    (EMPLOYMENT_STATUS_UNEMPLOYED, "Not employed"),
)

INVITATION_ADVISOR = 0
AUTHORIZED_REPRESENTATIVE = 1
INVITATION_SUPERVISOR = 2
INVITATION_CLIENT = 3
INVITATION_TYPE_CHOICES = (
    (INVITATION_ADVISOR, "Advisor"),
    (AUTHORIZED_REPRESENTATIVE, 'Authorised representative'),
    (INVITATION_SUPERVISOR, 'Supervisor'),
    (INVITATION_CLIENT, 'Client'),
)

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

ASSET_FEE_EVENTS = ((0, 'Day End'),
                    (1, 'Complete Day'),
                    (2, 'Month End'),
                    (3, 'Complete Month'),
                    (4, 'Fiscal Month End'),
                    (5, 'Entry Order'),
                    (6, 'Entry Order Item'),
                    (7, 'Exit Order'),
                    (8, 'Exit Order Item'),
                    (9, 'Transaction'))

ASSET_FEE_UNITS = ((0, 'Asset Value'),  # total value of the asset
                   (1, 'Asset Qty'),  # how many units of an asset
                   (2, 'NAV Performance'))  # % positive change in the NAV

ASSET_FEE_LEVEL_TYPES = (
    (0, 'Add'),  # Once the next level is reached, the amount form that band is added to lower bands
    (1, 'Replace')  # Once the next level is reached, the value from that level is used for the entire amount
)

# TODO: Make the system currency a setting for the site
SYSTEM_CURRENCY = 'AUD'

BONDS = "BONDS"  # Bonds only Fund
STOCKS = "STOCKS"  # Stocks only Fund
MIXED = "MIXED"  # Mixture of stocks and bonds
INVESTMENT_TYPES = (("BONDS", "BONDS"), ("STOCKS", "STOCKS"), ("MIXED", "MIXED"))

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
    ("FIXED_INCOME_CN", "FIXED_INCOME_CN"))


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
        except User.DoesNotExist:
            user = None

        if (user is not None) and (not user.prepopulated):
            # confirm password
            if not user.check_password(password1):
                self._errors['email'] = mark_safe(u'<ul class="errorlist"><li>User already exists</li></ul>')
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
        except User.DoesNotExist:
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
    def states_codes(self):
        states = []
        for item in self._meta.get_field('state').choices:
            states.append({"db_value": item[0], "name": item[1]})
        return states

    @property
    def email(self):
        return self.user.email


class AssetFeePlan(models.Model):
    """
    To calculate the fees for an asset and client, get the AssetFeePlan for the account, then lookup on the AssetFee
    model for all the fees applicable for the Asset and Plan.
    """
    name = models.CharField(max_length=127, unique=True)
    description = models.TextField(null=True)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


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

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def is_advisor(self):
        """
        Custom helper method for User class to check user type/profile.
        """
        if not hasattr(self, '_is_advisor'):
            self._is_advisor = hasattr(self, 'advisor')
            #self._is_advisor = self.groups.filter(name=User.GROUP_ADVISOR).exists()

        return self._is_advisor

    @property
    def is_client(self):
        """
        Custom helper method for User class to check user type/profile.
        """
        if not hasattr(self, '_is_client'):
            self._is_client = hasattr(self, 'client')
            #self._is_client = self.groups.filter(name=User.GROUP_CLIENT).exists()

        return self._is_client

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        " Returns the short name for the user."
        return self.first_name

    def get_token(self):
        """
        Custom helper method for User class to get user token.
        see: rest_framework.authentication.TokenAuthentication
        """
        if not hasattr(self, '_token'):
            try:
                self._token, _ = Token.objects.get_or_create(user=self)

            except IntegrityError:
                # hint: threading and concurrency makes me sick
                self._token = Token.objects.get(user=self)

        return self._token

    def email_user(self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class AssetClass(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[0-9a-zA-Z_]+$',
            message="Invalid character only accept (0-9a-zA-Z_) ")],
        db_index=True)
    display_order = models.PositiveIntegerField(db_index=True)
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True,
                                               default="",
                                               null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
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


class PortfolioSet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    asset_classes = models.ManyToManyField(AssetClass, related_name='portfolio_sets')
    risk_free_rate = models.FloatField()

    # Also has 'views' from View model.

    @property
    def stocks_and_bonds(self):
        has_bonds = False
        has_stocks = False

        for asset_class in self.asset_classes.all():
            if "EQUITY_" in asset_class.super_asset_class:
                has_stocks = True
            if "FIXED_INCOME_" in asset_class.super_asset_class:
                has_bonds = True

        if has_bonds and has_stocks:
            return "both"
        elif has_stocks:
            return "stocks"
        else:
            return "bonds"

    @property
    def regions(self):
        def get_regions(x):
            return x.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
        return [get_regions(asset_class.super_asset_class) for asset_class in self.asset_classes.all()]

    @property
    def regions_currencies(self):
        rc = {}

        def get_regions_currencies(asset):
            region = asset.super_asset_class.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
            if region not in rc:
                rc[region] = "AUD"
            ticker = asset.tickers.filter(ordering=0).first()
            if ticker:
                if ticker.currency != "AUD":
                    rc[region] = ticker.currency
            else:
                logger.warn("Asset class: {} has no tickers.".format(asset.name))

        for asset_class in self.asset_classes.all():
            get_regions_currencies(asset_class)
        return rc

    def __str__(self):
        return self.name


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
    default_portfolio_set = models.ForeignKey(PortfolioSet)

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
    def total_revenue(self):
        total = 0
        for advisor in self.advisors.all():
            total += advisor.total_revenue
        return total

    @property
    def total_invested(self):
        total = 0
        for advisor in self.advisors.all():
            total += advisor.total_invested
        return total

    @property
    def total_return(self):
        if self.total_invested > 0:
            return self.total_revenue / self.total_invested
        return 0

    @property
    def total_fees(self):
        total = 0
        for advisor in self.advisors.all():
            total += advisor.total_fees
        return total

    @property
    def total_balance(self):
        total = 0
        for advisor in self.advisors.all():
            total += advisor.total_balance
        return total

    @property
    def total_account_groups(self):
        total = 0
        for advisor in self.advisors.all():
            total += advisor.total_account_groups
        return total

    @property
    def average_balance(self):
        if self.total_account_groups > 0:
            return self.total_balance / self.total_account_groups
        return 0

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
    last_action = models.DateTimeField(null=True)
    default_portfolio_set = models.ForeignKey(PortfolioSet)

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
        except User.DoesNotExist:
            user = None

        invitation_url = settings.SITE_URL + "/" + self.firm.slug + "/client/signup/" + self.token

        if user:
            invitation_url += "/" + str(user.pk) + "/" + user.client.primary_accounts.first().token
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
    def client_accounts(self):
        accounts = []
        for household in self.households:
            all_accounts = household.accounts.all()
            accounts.extend(all_accounts)
        return accounts

    @property
    def total_balance(self):
        b = 0
        for ag in self.households:
            b += ag.total_balance

        return b

    @property
    def primary_clients_size(self):
        return len(Client.objects.filter(advisor=self, user__prepopulated=False))

    @property
    def secondary_clients_size(self):
        return len(Client.objects.filter(secondary_advisors__in=[self], user__prepopulated=False).distinct())

    @property
    def total_fees(self):
        return 0

    @property
    def total_revenue(self):
        return 0

    @property
    def total_invested(self):
        return 0

    @property
    def total_return(self):
        if self.total_invested > 0:
            return self.total_revenue / self.total_invested
        return 0

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
    """
    We use the term 'Households' on the Advisor page for this as well.
    """

    advisor = models.ForeignKey(Advisor,
                                related_name="primary_account_groups",
                                on_delete=PROTECT  # Must reassign account groups before removing advisor
                               )
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


ACCOUNT_TYPE_PERSONAL = 0
ACCOUNT_TYPE_JOINT = 1
ACCOUNT_TYPE_TRUST = 2
ACCOUNT_TYPE_SMSF = 3
ACCOUNT_TYPE_CORPORATE = 4
ACCOUNT_TYPES = (
    (ACCOUNT_TYPE_PERSONAL, "Personal Account"),
    (ACCOUNT_TYPE_JOINT, "Joint Account"),
    (ACCOUNT_TYPE_TRUST, "Trust Account"),
    (ACCOUNT_TYPE_SMSF, "Self Managed Superannuation Fund"),
    (ACCOUNT_TYPE_CORPORATE, "Corporate Account"),
)


class ClientAccount(models.Model):
    account_group = models.ForeignKey(AccountGroup,
                                      related_name="accounts_all",
                                      null=True)
    custom_fee = models.PositiveIntegerField(default=0)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES)
    account_name = models.CharField(max_length=255, default='PERSONAL')
    primary_owner = models.ForeignKey('Client', related_name="primary_accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=36, editable=False)
    confirmed = models.BooleanField(default=False)
    tax_loss_harvesting_consent = models.BooleanField(default=False)
    tax_loss_harvesting_status = models.CharField(max_length=255, choices=(("USER_OFF", "USER_OFF"),
                                                                           ("USER_ON", "USER_ON")), default="USER_OFF")
    asset_fee_plan = models.ForeignKey(AssetFeePlan, null=True)
    default_portfolio_set = models.ForeignKey(PortfolioSet)
    cash_balance = models.FloatField(default=0, help_text='The amount of cash in this account available to be used.')

    objects = ClientAccountQuerySet.as_manager()

    @property
    def goals(self):
        return self.all_goals.filter(archived=False)

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
    def advisors(self):
        return chain([self.primary_owner.advisor, self.account_group.advisor], self.account_group.secondary_advisors.all())

    @property
    def target(self):
        total_target = 0
        for goal in self.goals.all():
            total_target += goal.target
        return total_target

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
    def goals_length(self):
        return len(self.goals.all())

    @property
    def get_term(self):
        total_term = 0
        goals_with_term = 0
        for goal in self.goals.all():
            goal_term = goal.get_term
            if goal_term != 0:
                total_term += goal_term
                goals_with_term += 1
        if goals_with_term == 0:
            return 0
        return total_term / goals_with_term

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


class JointAccount(models.Model):
    joined = models.ForeignKey(ClientAccount,
                               related_name='joint_holder',
                               # Delete an account and you delete any joint accounts they are joined with
                               on_delete=CASCADE,
                              )
    client = models.ForeignKey('Client',
                               related_name='joint_accounts',
                               on_delete=CASCADE,  # Delete a client, you delete any joint accounts they are a part of
                              )


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
    advisor = models.ForeignKey(Advisor,
                                related_name="all_clients",
                                on_delete=PROTECT,  # Must reassign clients before removing advisor
                               )
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

    employment_status = models.IntegerField(choices=EMPLOYMENT_STATUSES)
    net_worth = models.FloatField(verbose_name="Net worth ($)", default=0)
    income = models.FloatField(verbose_name="Income ($)", default=0)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    employer = models.CharField(max_length=255, null=True, blank=True)
    betasmartz_agreement = models.BooleanField(default=False)
    advisor_agreement = models.BooleanField(default=False)
    last_action = models.DateTimeField(null=True)

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
    def accounts_all(self):
        # TODO: Make this work
        #return self.primary_accounts.get_queryset() | self.joint_accounts.select_related('joined')
        return self.primary_accounts

    @property
    def accounts(self):
        return self.accounts_all.filter(confirmed=True)

    @property
    def get_financial_plan(self):
        if hasattr(self, 'financial_plan'):
            plan = self.financial_plan
        else:
            return ""

        if plan is None:
            return ""
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


class MarkowitzScale(models.Model):
    """
    We convert the max and min Markowitz to an exponential function in the form a * b^x + c passing through the points:
    [(-50, min), (0, 1.2), (50, max)]
    So the risk slider is exponential.
    """
    date = models.DateField(unique=True)
    min = models.FloatField()
    max = models.FloatField()
    a = models.FloatField(null=True)
    b = models.FloatField(null=True)
    c = models.FloatField(null=True)


class Region(models.Model):
    name = models.CharField(max_length=127, blank=False, null=False, help_text='Name of the region')
    description = models.TextField(blank=True, default="", null=False)

    def __str__(self):
        return self.name


class FinancialInstrument(models.Model):
    """
    A financial instrument is an identifiable thing for which data can be gathered to generate a daily return.
    """
    class Meta:
        abstract = True

    display_name = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    description = models.TextField(blank=True, default="", null=False)
    url = models.URLField()
    currency = models.CharField(max_length=10, default="AUD")
    region = models.ForeignKey(Region)
    data_api = models.CharField(help_text='The module that will be used to get the data for this ticker',
                                choices=[('portfolios.api.bloomberg', 'Bloomberg')],
                                max_length=30,
                                null=True)
    data_api_param = models.CharField(help_text='Structured parameter string appropriate for the data api. The '
                                                'first component would probably be id appropriate for the given api',
                                      unique=True,
                                      max_length=30,
                                      null=True)

    def __str__(self):
        return self.display_name


class MarketIndex(FinancialInstrument):
    """
    For the moment, an index is a concrete FinancialInstrument that may have one or more tickers(funds) that track it.
    """
    trackers = GenericRelation('Ticker')
    daily_prices = GenericRelation('DailyPrice',
                                   content_type_field='instrument_content_type',
                                   object_id_field='instrument_object_id')
    market_caps = GenericRelation('MarketCap',
                                  content_type_field='instrument_content_type',
                                  object_id_field='instrument_object_id')

    def get_returns(self, start_date, end_date):
        """
        Get the longest available consecutive daily returns series from the end date.
        :param start_date:
        :param end_date:
        :return: A pandas time-series of the returns
        """
        return get_price_returns(self, start_date, end_date)


class Ticker(FinancialInstrument):
    symbol = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        unique=True,
        validators=[RegexValidator(regex=r'^[^ ]+$',
                                   message="Invalid symbol format")])
    ordering = models.IntegerField(db_index=True)
    unit_price = models.FloatField(default=10)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")
    ethical = models.BooleanField(default=False,
                                  help_text='Is this an ethical instrument?')
    etf = models.BooleanField(default=True,
                              help_text='Is this an Exchange Traded Fund (True) or Mutual Fund (False)?')
    # A benchmark should be a subclass of financial instrument
    limit = models.Q(app_label='main', model='marketindex')  # Only using index benchmarks at the moment, but may do more later
    # TODO: REmove this null bit
    benchmark_content_type = models.ForeignKey(ContentType,
                                               on_delete=models.CASCADE,
                                               null=True,
                                               limit_choices_to=limit,
                                               verbose_name='Benchmark Type')
    benchmark_object_id = models.PositiveIntegerField(null=True,
                                                      verbose_name='Benchmark Instrument')
    benchmark = GenericForeignKey('benchmark_content_type', 'benchmark_object_id')
    daily_prices = GenericRelation('DailyPrice',
                                   content_type_field='instrument_content_type',
                                   object_id_field='instrument_object_id')

    # Also may have 'features' property from the AssetFeatureValue model.

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

    def get_returns(self, start_date, end_date):
        """
        Get the longest available consecutive daily returns series from the end date.
        :param start_date:
        :param end_date:
        :return: A pandas time-series of the returns
        """
        return get_price_returns(self, start_date, end_date)

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
    inviter_object = GenericForeignKey('inviter_type', 'inviter_id')
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
        except User.DoesNotExist:
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
    portfolio_set = models.ForeignKey(PortfolioSet)
    api = models.CharField(max_length=20,
                           default=YAHOO_API,
                           choices=API_CHOICES)

    def __str__(self):
        return "BetaSmartz"


class Dividend(models.Model):
    class Meta:
        unique_together = ("instrument", "record_date")

    instrument = models.ForeignKey(Ticker)
    record_date = models.DateTimeField()
    amount = models.FloatField(validators=[MinValueValidator(0.0)],
                               help_text="Amount of the dividend in system currency")
    franking = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                                 help_text="Franking percent. 0.01 = 1% of the dividend was franked.")


class FiscalYear(models.Model):
    name = models.CharField(max_length=127)
    year = models.IntegerField()
    begin_date = models.DateField(help_text="Inclusive begin date for this fiscal year")
    end_date = models.DateField(help_text="Inclusive end date for this fiscal year")
    month_ends = models.CommaSeparatedIntegerField(max_length=35,
                                                   validators=[MinLengthValidator(23)],
                                                   help_text="Comma separated month end days each month of the year. First element is January.")


class Company(models.Model):
    name = models.CharField(max_length=127)
    fiscal_years = models.ManyToManyField(FiscalYear)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


_asset_fee_ht = "List of level transition points and the new values after that transition. Eg. '0: 0.001, 10000: 0.0'"


class AssetFee(models.Model):
    name = models.CharField(max_length=127)
    plan = models.ForeignKey(AssetFeePlan)
    collector = models.ForeignKey(Company)
    asset = models.ForeignKey(Ticker)
    applied_per = models.IntegerField(choices=ASSET_FEE_EVENTS)
    fixed_level_unit = models.IntegerField(choices=ASSET_FEE_UNITS)
    fixed_level_type = models.IntegerField(choices=ASSET_FEE_LEVEL_TYPES)
    fixed_levels = models.TextField(help_text=_asset_fee_ht)
    prop_level_unit = models.IntegerField(choices=ASSET_FEE_UNITS)
    prop_apply_unit = models.IntegerField(choices=ASSET_FEE_UNITS)
    prop_level_type = models.IntegerField(choices=ASSET_FEE_LEVEL_TYPES)
    prop_levels = models.TextField(help_text=_asset_fee_ht)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class GoalType(models.Model):
    name = models.CharField(max_length=255, null=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    default_term = models.IntegerField(null=False)
    group = models.CharField(max_length=255, null=True)
    risk_sensitivity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
                                         help_text="Default risk sensitivity for this goal type. "
                                                   "0 = not sensitive, 10 = Very sensitive (No risk tolerated)")

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class RecurringTransaction(models.Model):
    # Note: Only settings that are active will have their recurring transactions processed.
    setting = models.ForeignKey('GoalSetting', related_name='recurring_transactions', null=True)  # TODO remove the null
    # Note: https://www.npmjs.com/package/rrule and https://www.npmjs.com/package/rrecur for UI side of below
    recurrence = models.TextField()
    enabled = models.BooleanField(default=True)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_transaction(self):
        return self.recurrence.after(datetime.datetime.now(), inc=True)

    @staticmethod
    def get_events(recurring_transactions, start, end):
        """
        :param start: A datetime for the start
        :param end: A datetime for the end
        :param recurring_transactions:
        :return: a list of (date, amount) tuples for all the recurring transaction events between the given dates.
        Not guarateed to return them in sorted order.
        """
        res = []
        for r in recurring_transactions.all():
            if not r.enabled:
                continue
            rrule = deserialize(r.recurrence)
            res.extend(zip(rrule.between(start, end), repeat(r.amount)))
        return res


class Portfolio(models.Model):
    setting = models.OneToOneField('GoalSetting', related_name='portfolio')
    stdev = models.FloatField()
    er = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    # Also has 'items' field from PortfolioItem


class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='items')
    asset = models.ForeignKey(Ticker)
    weight = models.FloatField()
    volatility = models.FloatField(help_text='variance of this asset at the time of creating this portfolio.')


class GoalSetting(models.Model):
    target = models.FloatField(default=0)
    completion = models.DateField(help_text='The scheduled completion date for the goal.')
    hedge_fx = models.BooleanField(help_text='Do we want to hedge foreign exposure?')
    metric_group = models.ForeignKey('GoalMetricGroup', related_name='settings')
    # also may have a 'recurring_transactions' field from RecurringTransaction model.
    # also may have a 'portfolio' field from Portfolio model. May be null if no portfolio has been assigned yet.

    @property
    def goal(self):
        if hasattr(self, 'goal_selected'):
            return self.goal_selected
        if hasattr(self, 'goal_approved'):
            return self.goal_approved
        # Must be an active goal
        return self.goal_active

    def __str__(self):
        return str(self.id)


class GoalMetricGroup(models.Model):
    TYPE_CUSTOM = 0
    TYPE_PRESET = 1
    TYPES = (
        (TYPE_CUSTOM, 'Custom'),  # Should be deleted when it is not used by any settings object
        (TYPE_PRESET, 'Preset'),  # Exists on it's own.
    )
    type = models.IntegerField(choices=TYPES, default=TYPE_CUSTOM)
    name = models.CharField(max_length=100, null=True)  #
    # also has field 'metrics' from GoalMetric
    # Also has field 'settings' from GoalSetting

    def constraint_inputs(self):
        """
        A comparable set of inputs to all the optimisation constraints that would be generated from this group.
        :return:
        """
        features = {}
        for metric in self.metrics.all():
            if metric.type == GoalMetric.METRIC_TYPE_RISK_SCORE:
                risk = metric.configured_val
            else:
                features[metric.feature] = (metric.comparison, metric.feature, metric.configured_val)
        return risk, features


class InvalidStateError(Exception):
    """
    If an action was attempted on a stateful object and the current state was not once of the valid ones for the action
    """
    def __init__(self, current, required):
        self.current = current
        self.required = required

    def __str__(self):
        return "Invalid state: {}. Should have been one of: {}".format(self.current, self.required)


class Goal(models.Model):
    class State(ChoiceEnum):
        # The goal is currently active and ready for action.
        ACTIVE = 0
        # A request to archive the goal has been made, but is waiting approval.
        # The goal can be reinstated by simply changing the state back to ACTIVE
        ARCHIVE_REQUESTED = 1
        # A request to archive the goal has been approved, and is currently in process.
        # No further actions can be performed on the goal to reactivate it.
        CLOSING = 2
        # The goal no longer owns any assets, and has a zero balance.
        # This goal is archived. No further actions can be performed on the goal
        ARCHIVED = 3

    account = models.ForeignKey(ClientAccount, related_name="all_goals")
    name = models.CharField(max_length=100)
    type = models.ForeignKey(GoalType)
    created = models.DateTimeField(auto_now_add=True)
    portfolio_set = models.ForeignKey(
        PortfolioSet,
        help_text='The set of assets that may be used to create a portfolio for this goal.')
    # The cash_balance field should NEVER be updated by an API. only our internal processes.
    cash_balance = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])

    active_settings = models.OneToOneField(
        GoalSetting,
        related_name='goal_active',
        help_text='The settings were last used to do a rebalance.'
                  'These settings are responsible for our current market positions.',
        blank=True,
        null=True)
    approved_settings = models.OneToOneField(
        GoalSetting,
        related_name='goal_approved',
        help_text='The settings that both the client and advisor have confirmed '
                  'and will become active the next time the goal is rebalanced.',
        blank=True,
        null=True)
    selected_settings = models.OneToOneField(
        GoalSetting,
        related_name='goal_selected',
        help_text='The settings that the client has confirmed, '
                  'but are not yet approved by the advisor.',
        blank=True,
        null=True)
    # Drift score is a cached field, and is populated whenever the goal is processed at the end-of-day process.
    # As such it should not be written to anywhere else than that.
    drift_score = models.FloatField(default=0.0, help_text='The maximum ratio of current drift to maximum allowable'
                                                           ' drift from any metric on this goal.')
    rebalance = models.BooleanField(default=True, help_text='Do we want to perform automated rebalancing on this goal?')
    state = models.IntegerField(choices=State.choices(), default=State.ACTIVE.value)
    supervised = models.BooleanField(default=True, help_text='Is this goal supervised by an advisor?')

    # Also has 'positions' field from Position model.

    objects = GoalQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '[' + str(self.id) + '] ' + self.name + " : " + self.account.primary_owner.full_name

    @transaction.atomic
    def archive(self):
        """
        Archives a goal, creating a closing order to neutralise any positions.
        :return: None
        """
        from main.ordering import OrderManager
        if self.State(self.state) != self.State.ARCHIVE_REQUESTED:
            raise InvalidStateError(self.State(self.state), self.State.ARCHIVE_REQUESTED)

        FinancialPlanAccount.objects.filter(account=self).delete()

        # Remove outstanding orders and close existing positions
        async_id = OrderManager.close_positions(self)

        self.state = self.State.ARCHIVED.value if async_id is None else self.State.CLOSING.value
        self.save()

    @transaction.atomic
    def set_selected(self, setting):
        """
        Sets the passed in setting object as the selected_setting.
        :param setting:
        :return:
        """
        old_setting = self.selected_settings
        if setting == old_setting:
            return
        self.selected_settings = setting
        self.save()
        if old_setting not in (self.active_settings, self.approved_settings):
            if old_setting.metric_group.type == GoalMetricGroup.TYPE_CUSTOM:
                # This will also delete the setting as the metric group is a foreign key.
                old_setting.metric_group.delete()

    @transaction.atomic
    def approve_selected(self):
        old_setting = self.approved_settings
        if self.selected_settings == old_setting:
            return
        self.approved_settings = self.selected_settings
        self.save()
        if old_setting != self.active_settings:
            old_setting.delete()

    @property
    def available_balance(self):
        return self.total_balance - self.pending_outgoings

    @property
    def pending_transactions(self):
        return Transaction.objects.filter(Q(to_goal=self) | Q(from_goal=self) & Q(status=Transaction.STATUS_PENDING))

    @property
    def pending_amount(self):
        pa = 0.0
        for t in self.pending_transactions:
            if self == t.from_goal:
                pa -= t.amount
            else:
                pa += t.amount
        return pa

    @property
    def pending_incomings(self):
        pd = 0.0
        for d in Transaction.objects.filter(to_goal=self, status=Transaction.STATUS_PENDING):
            pd += d.amount
        return pd

    @property
    def pending_outgoings(self):
        pw = 0.0
        for w in Transaction.objects.filter(from_goal=self, status=Transaction.STATUS_PENDING):
            pw += w.amount
        return pw

    @property
    def requested_incomings(self):
        pd = 0.0
        for d in Transaction.objects.filter(to_goal=self,
                                            status=Transaction.STATUS_EXECUTED).exclude(reason__in=(Transaction.REASON_FEE,
                                                                                                    Transaction.REASON_DIVIDEND)):
            pd += d.amount
        return pd

    @property
    def requested_outgoings(self):
        pw = 0.0
        for w in Transaction.objects.filter(from_goal=self,
                                            status=Transaction.STATUS_EXECUTED).exclude(reason__in=(Transaction.REASON_FEE,
                                                                                                    Transaction.REASON_DIVIDEND)):
            pw -= w.amount
        return pw

    @property
    def total_dividends(self):
        divs = 0.0
        for t in Transaction.objects.filter(Q(status=Transaction.STATUS_EXECUTED) &
                                            (Q(to_goal=self) | Q(from_goal=self)) &
                                            (Q(reason=Transaction.REASON_DIVIDEND))):
            divs += t.amount if self == t.to_goal else -t.amount
        return divs

    @property
    def market_changes(self):
        return 0.0

    @property
    def total_deposits(self):
        """
        :return: The total amount of the deposits into the goal from the account cash. Excluding pending.
        """
        inputs = 0.0
        for t in Transaction.objects.filter(status=Transaction.STATUS_EXECUTED,
                                            to_goal=self,
                                            reason=Transaction.REASON_DEPOSIT):
            inputs += t.amount
        return inputs

    @property
    def total_withdrawals(self):
        """
        :return: The total amount of the withdrawals from the goal to the account cash. Excluding pending.
        """
        inputs = 0.0
        for t in Transaction.objects.filter(status=Transaction.STATUS_EXECUTED,
                                            to_goal=self,
                                            reason=Transaction.REASON_WITHDRAWAL):
            inputs += t.amount
        return inputs

    @property
    def net_invested(self):
        """
        :return: The actual realised amount invested (incomings - outgoings),
                 excluding any pending transactions or performance-based transactions.

        """
        inputs = 0.0
        for t in Transaction.objects.filter(Q(status=Transaction.STATUS_EXECUTED) &
                                            (Q(to_goal=self) | Q(from_goal=self)) &
                                            (~Q(reason__in=(Transaction.REASON_FEE, Transaction.REASON_DIVIDEND)))):
            inputs += t.amount if self == t.to_goal else -t.amount
        return inputs

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
    def total_fees(self):
        fees = 0.0
        for t in Transaction.objects.filter(Q(status=Transaction.STATUS_EXECUTED) &
                                            (Q(to_goal=self) | Q(from_goal=self)) &
                                            (Q(reason=Transaction.REASON_FEE))):
            fees += t.amount if self == t.to_goal else -t.amount
        return fees

    @property
    def recharacterized(self):
        return 0

    @property
    def total_earnings(self):
        """
        Earnings after fees. (increase of value, plus dividends, minus fees)
        :return: The current total balance minus any inputs excluding dividends, plus any withdrawals excluding fees.
        """
        return self.total_balance - self.net_invested

    @property
    def investments(self):
        return {
            'deposits': self.total_deposits,
            'withdrawals': self.total_withdrawals,
            'other': self.net_invested - self.total_deposits + self.total_withdrawals,
            'net_pending': self.pending_amount,
        }

    @property
    def earnings(self):
        return {
                'market_moves': self.total_earnings - self.total_dividends + self.total_fees,
                'dividends': self.total_dividends,
                'fees': self.total_fees,
               }

    def balance_at(self, future_dt, confidence=0.5):
        """
        Calculates the predicted balance at the given date with the given confidence based on the current
        selected-settings.
        :param date: The date to get the predicted balance for.
        :param confidence: The confidence level to get the prediction at.
        :return: Float predicted balance.
        """
        # If we don't have a selected portfolio, we can say nothing, so return the current balance
        if self.selected_settings is None:
            return self.total_balance

        # Get the z-multiplier for the given confidence
        z_mult = -st.norm.ppf(confidence)

        # If no portfolio has been calculated, er and stdev are assumed 0.
        if not hasattr(self.selected_settings, 'portfolio'):
            er = 1.0
            stdev = 0.0
        else:
            er = 1 + self.selected_settings.portfolio.er
            stdev = self.selected_settings.portfolio.stdev

        now = datetime.datetime.now()
        # Get the predicted cash-flow events until the provided future date
        cf_events = [(now, self.total_balance)]
        if hasattr(self.selected_settings, 'recurring_transactions'):
            cf_events += RecurringTransaction.get_events(self.selected_settings.recurring_transactions,
                                                         now,
                                                         datetime.datetime.combine(future_dt, datetime.time()))

        # TODO: Add estimated fee events to this.

        # Calculate the predicted_balance based on cash flow events, er, stdev and z_mult
        predicted = 0
        for dt, val in cf_events:
            tdelta = dt - now
            y_delta = (tdelta.days + tdelta.seconds/86400.0)/365.2425
            predicted += val * (er ** y_delta + z_mult * stdev * (y_delta ** 0.5))

        return predicted

    @property
    def on_track(self):
        if self.selected_settings is None:
            return False

        # If we don't have a target or completion date, we have no concept of OnTrack.
        if self.selected_settings.target is None or self.selected_settings.completion is None:
            return False

        predicted_balance = self.balance_at(self.selected_settings.completion)
        return predicted_balance >= self.selected_settings.target

    @property
    def total_balance(self):
        b = self.cash_balance
        for p in Position.objects.filter(goal=self).all():
            b += p.value
        return b

    @property
    def current_balance(self):
        """
        :return: The current total balance including any pending transactions.
        """
        return self.total_balance + self.pending_amount

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
        """
        :return: The Time-Weighted Return for this goal
        """
        # TODO: Do it
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
    def get_term(self):
        today = date.today()
        # check if goal is part of the retirement plan
        financial_plan_accounts = self.account.primary_owner.financial_plan_accounts.filter(account=self).all()
        if financial_plan_accounts:
            retirement_age = self.account.primary_owner.financial_plan.retirement_age
            current_age = today.year - self.account.primary_owner.date_of_birth.year
            term = retirement_age - current_age
            if term > 0:
                return term
            return 0

        else:
            term = self.completion_date.year - today.year
            return term

    @property
    def auto_term(self):
        today = date.today()
        return "{0}y".format(self.get_term)


class HistoricalBalance(models.Model):
    """
    The historical balance model is a cache of the information that can be built from the Execution and Transaction
    models. It enables fast historical view of a goals's balance.
    This model should only ever be updated by code, and calculated from the source data in the Execution and Transaction
    models.
    """
    goal = models.ForeignKey(Goal, related_name='balance_history')
    date = models.DateField()
    balance = models.FloatField()


class AssetFeature(models.Model):
    name = models.CharField(max_length=127, unique=True, help_text="This should be a noun such as 'Region'.")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class AssetFeatureValue(models.Model):
    name = models.CharField(max_length=127, unique=True, help_text="This should be an adjective.")
    description = models.TextField(blank=True, null=True, help_text="A clarification of what this value means.")
    feature = models.ForeignKey(AssetFeature,
                                related_name='values',
                                help_text="The asset feature this is one value for.")
    assets = models.ManyToManyField(Ticker, related_name='features')

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class GoalMetric(models.Model):
    """
    A goal metric can currently be used to:
     - Specify what percentage of assets in a goal should have a particular feature, or -
     - Specify what risk score is desired for a goal. This is the normalised risk score range (0-1)
    For example:
        "Minimum 30% of my portfolio should be Australian, and rebalance whenever it becomes proportionally 5% different"
        {
            type: 0 (Portfolio Mix)
            feature: 1 (or whatever the ID is for the "Australian" feature value),
            comparison: 0 (Minimum),
            rebalance_type: 1,
            rebalance_thr: 0.05,
            configured_val: 0.3
        }
    """
    METRIC_TYPE_PORTFOLIO_MIX = 0
    METRIC_TYPE_RISK_SCORE = 1
    METRIC_COMPARISON_MINIMUM = 0
    METRIC_COMPARISON_EXACTLY = 1
    METRIC_COMPARISON_MAXIMUM = 2
    metric_types = {
        METRIC_TYPE_PORTFOLIO_MIX: 'Portfolio Mix',
        METRIC_TYPE_RISK_SCORE: 'RiskScore'
    }
    comparisons = {
        METRIC_COMPARISON_MINIMUM: 'Minimum',
        METRIC_COMPARISON_EXACTLY: 'Exactly',
        METRIC_COMPARISON_MAXIMUM: 'Maximum',
    }
    REBALANCE_TYPE_ABSOLUTE = 0
    REBALANCE_TYPE_RELATIVE = 1
    rebalance_types = {
        REBALANCE_TYPE_ABSOLUTE: 'Absolute',
        REBALANCE_TYPE_RELATIVE: 'Relative',
    }

    group = models.ForeignKey('GoalMetricGroup', related_name='metrics')
    type = models.IntegerField(choices=metric_types.items())
    feature = models.ForeignKey(AssetFeatureValue, null=True)
    comparison = models.IntegerField(default=1, choices=comparisons.items())
    rebalance_type = models.IntegerField(choices=rebalance_types.items(),
                                         help_text='Is the rebalance threshold an absolute threshold or relative (percentage difference) threshold?')
    rebalance_thr = models.FloatField(
        help_text='The difference between configured and measured value at which a rebalance will be recommended.')
    configured_val = models.FloatField(help_text='The value of the metric that was configured.')
    measured_val = models.FloatField(help_text='The latest measured value of the metric', null=True)

    @property
    def drift_score(self):
        """
        Drift score is a multiplier of how many times the rebalance trigger level the current difference between the
        measured value and configured value is. The range will typically be [-1.0,1.0], but may extend higher or lower
        under extreme drift situations.
        Our rebalancing aims to keep the drift score for a goal between [-1.0,1.0].
        :return: Float - The drift score
        """
        if self.measured_val is None:
            return 0.0

        if self.rebalance_type == self.REBALANCE_TYPE_ABSOLUTE:
            return self.rebalance_thr / (self.measured_val - self.configured_val)
        else:
            return self.rebalance_thr / ((self.measured_val - self.configured_val) / self.self.configured_val)

    def __str__(self):
        if self.type == 0:
            return "[{}] {} {}% {} for Metric: {}".format(self.id,
                                                          self.comparisons[self.comparison],
                                                          self.configured_val * 100,
                                                          self.feature.name,
                                                          self.id)
        else:
            return "[{}] Risk Score {} {} for Metric: {}".format(self.id,
                                                                 self.comparisons[self.comparison],
                                                                 1 + self.configured_val * 99,
                                                                 self.id)


class Position(models.Model):
    class Meta:
        unique_together = ('goal', 'ticker')

    goal = models.ForeignKey(Goal, related_name='positions')
    ticker = models.ForeignKey(Ticker)
    share = models.FloatField(default=0)

    @property
    def is_stock(self):
        return self.ticker.is_stock

    @property
    def value(self):
        return self.share * self.ticker.unit_price

    def __str__(self):
        return self.ticker.symbol


class MarketOrderRequest(models.Model):
    """
    A Market Order Request defines a request for an order to buy or sell one or more assets on a market.
    """
    class State(ChoiceEnum):
        PENDING = 0  # Raised somehow, but not yet approved to send to market
        APPROVED = 1  # Approved to send to market, but not yet sent.
        SENT = 2  # Sent to the broker (at least partially outstanding).
        CANCEL_PENDING = 3 # Sent, but have also sent a cancel
        COMPLETE = 4  # May be fully or partially executed, but there is none left outstanding.

    # The list of Order states that are still considered open.
    OPEN_STATES = [State.PENDING.value, State.APPROVED.value, State.SENT.value]

    state = models.IntegerField(choices=State.choices(), default=State.PENDING.value)
    account = models.ForeignKey('ClientAccount', related_name='market_orders', on_delete=PROTECT)
    # Also has 'execution_requests' field showing all the requests that went into this one order.
    # Also has 'executions' once the request has had executions.

    def __str__(self):
        return "[{}] - {}".format(self.id, self.State(self.state).name)

    def __repr__(self):
        return {
            'state': self.state,
            'account': self.account,
            'execution_requests': list(self.execution_requests) if hasattr(self, 'execution_requests') else [],
            'executions': list(self.executions) if hasattr(self, 'executions') else [],
        }

class ExecutionRequest(models.Model):
    """
    An execution request should be immutable. It should not be modified after creation. It can only be
    """
    class Reason(ChoiceEnum):
        DRIFT = 0  # The Request was made to neutralise drift on the goal
        WITHDRAWAL = 1  # The request was made because a withdrawal was requested from the goal.
        DEPOSIT = 2  # The request was made because a deposit was made to the goal
        METRIC_CHANGE = 3  # The request was made because the inputs to the optimiser were changed.

    reason = models.IntegerField(choices=Reason.choices())
    goal = models.ForeignKey('Goal', related_name='execution_requests', on_delete=PROTECT)
    asset = models.ForeignKey('Ticker', related_name='execution_requests', on_delete=PROTECT)
    volume = models.FloatField(help_text="Will be negative for a sell.")
    order = models.ForeignKey(MarketOrderRequest, related_name='execution_requests')
    # transaction can be null because once the request is complete, the transaction is removed.
    transaction = models.OneToOneField('Transaction', related_name='execution_request', null=True)

    def __repr__(self):
        return {
            'reason': str(self.reason),
            'goal': str(self.goal),
            'asset': str(self.ticker),
            'volume': self.volume
        }


class Execution(models.Model):
    """
    - The time the execution was processed (The time the cash balance on the goal was updated) is the 'executed' time
      on the related transaction.
    """
    asset = models.ForeignKey('Ticker', related_name='executions', on_delete=PROTECT)
    volume = models.FloatField(help_text="Will be negative for a sell.")
    order = models.ForeignKey(MarketOrderRequest, related_name='executions', on_delete=PROTECT)
    price = models.FloatField(help_text="The raw price paid/received per share. Not including fees etc.")
    executed = models.DateTimeField(help_text='The time the trade was executed.')
    amount = models.FloatField(help_text="The realised amount that was transferred into the account (specified on the "
                                         "order) taking into account external fees etc.")
    # Also has field 'distributions' from the ExecutionDistribution model describing to what goals this execution was
    # distributed


class ExecutionDistribution(models.Model):
    # One execution can contribute many distributions.
    execution = models.ForeignKey('Execution', related_name='distributions', on_delete=PROTECT)
    transaction = models.OneToOneField('Transaction', related_name='execution_distribution', on_delete=PROTECT)
    volume = models.FloatField(help_text="The number of units from the execution that were applied to the transaction.")


class Transaction(models.Model):
    """
    A transaction is a flow of funds to or from a goal.
    Deposits have a to_goal, withdrawals have a from_goal, transfers have both
    Every Transaction must have one or both.
    When one is null, it means it was to/from the account's cash.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_EXECUTED = 'EXECUTED'
    STATUSES = (('PENDING', 'PENDING'), ('EXECUTED', 'EXECUTED'))

    REASON_DIVIDEND = 0
    REASON_DEPOSIT = 1
    REASON_WITHDRAWAL = 2
    REASON_REBALANCE = 3
    REASON_TRANSFER = 4
    REASON_FEE = 5
    # Transaction is for a MarketOrderRequest. It's a transient transaction, for reserving funds. It will always be pending.
    # It will have it's amount reduced over time (converted to executions or rejections) until it's eventually removed.
    REASON_ORDER = 6
    REASON_EXECUTION = 7  # Transaction is for an Asset Execution that occurred. Will always be in executed state.
    REASONS = (
        (REASON_DIVIDEND, "DIVIDEND"),  # Dividend re-investment from an asset owned by the goal
        (REASON_DEPOSIT, "DEPOSIT"),  # Deposit from the account to the goal
        (REASON_WITHDRAWAL, 'WITHDRAWAL'),  # Withdrawal from the goal to the account
        (REASON_REBALANCE, 'REBALANCE'),  # As part of a rebalance, we may transfer from goal to goal.
        (REASON_TRANSFER, 'TRANSFER'),  # Amount transferred from one goal to another.
        (REASON_FEE, 'FEE'),
        (REASON_ORDER, 'ORDER'),
        (REASON_EXECUTION, 'EXECUTION'),
    )
    # The set of Transaction reasons that are considered investor cash flow in or out of the goal.
    CASH_FLOW_REASONS = [REASON_DEPOSIT, REASON_WITHDRAWAL, REASON_REBALANCE, REASON_TRANSFER]

    reason = models.IntegerField(choices=REASONS, db_index=True)
    from_goal = models.ForeignKey(Goal,
                                  related_name="transactions_from",
                                  null=True,
                                  blank=True,
                                  db_index=True,
                                  on_delete=PROTECT  # Cannot remove a goal that has transactions
                                 )
    to_goal = models.ForeignKey(Goal,
                                related_name="transactions_to",
                                null=True,
                                blank=True,
                                db_index=True,
                                on_delete=PROTECT  # Cannot remove a goal that has transactions
                               )
    amount = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_PENDING)
    created = models.DateTimeField(auto_now_add=True)
    executed = models.DateTimeField(null=True)

    # May also have 'execution_request' field from the ExecutionRequest model if it has reason ORDER
    # May also have 'execution_distribution' field from the ExecutionDistribution model if it has reason EXECUTION

    def save(self, *args, **kwargs):
        if self.from_goal is None and self.to_goal is None:
            raise ValidationError("One or more of from_goal and to_goal is required")
        if self.from_goal == self.to_goal:
            raise ValidationError("Cannot transact with myself.")
        super(Transaction, self).save(*args, **kwargs)


class DataApiDict(models.Model):
    api = models.CharField(choices=API_CHOICES, max_length=50)
    platform_symbol = models.CharField(max_length=20)
    api_symbol = models.CharField(max_length=20)


class TransactionMemo(models.Model):
    category = models.CharField(max_length=255)
    comment = models.TextField()
    transaction_type = models.CharField(max_length=20)
    transaction = models.ForeignKey(Transaction,
                                    related_name="memos",
                                    on_delete=CASCADE,  # Delete any memos where there is no longer a transaction
                                   )


class SymbolReturnHistory(models.Model):
    return_number = models.FloatField(default=0)
    symbol = models.CharField(max_length=20)
    date = models.DateField()


PERFORMER_GROUP_STRATEGY = "PERFORMER_GROUP_STRATEGY"
PERFORMER_GROUP_BENCHMARK = "PERFORMER_GROUP_BENCHMARK"
PERFORMER_GROUP_BOND = "PERFORMER_GROUP_BOND"
PERFORMER_GROUP_STOCK = "PERFORMER_GROUP_STOCK"
PERFORMER_GROUP_CHOICE = (
    (PERFORMER_GROUP_STRATEGY, "PERFORMER_GROUP_STRATEGY"),
    (PERFORMER_GROUP_BENCHMARK, "PERFORMER_GROUP_BENCHMARK"),
    (PERFORMER_GROUP_BOND, "PERFORMER_GROUP_BOND"),
    (PERFORMER_GROUP_STOCK, "PERFORMER_GROUP_STOCK")
)


class Performer(models.Model):
    symbol = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=20,
                             choices=PERFORMER_GROUP_CHOICE,
                             default=PERFORMER_GROUP_BENCHMARK)
    allocation = models.FloatField(default=0)
    #portfolio_set = models.ForeignKey(PortfolioSet)
    portfolio_set = models.IntegerField()


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


class DailyPrice(models.Model):
    """
    If a Financial Instrument is tradable, it will have a price.
    """
    objects = DataFrameManager()

    class Meta:
        unique_together = ("instrument_content_type", "instrument_object_id", "date")

    # An instrument should be a subclass of financial instrument
    # TODO: REmove this null bit
    instrument_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    instrument_object_id = models.PositiveIntegerField(null=True)
    instrument = GenericForeignKey('instrument_content_type', 'instrument_object_id')
    date = models.DateField()
    price = models.FloatField(null=True)


class MarketCap(models.Model):
    """
    If a Financial Instrument is tradable, it will have a market capitalisation. This may not change often.
    """
    objects = DataFrameManager()

    class Meta:
        unique_together = ("instrument_content_type", "instrument_object_id", "date")

    # An instrument should be a subclass of financial instrument
    # TODO: Remove this null bit
    instrument_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    instrument_object_id = models.PositiveIntegerField(null=True)
    instrument = GenericForeignKey('instrument_content_type', 'instrument_object_id')
    # TODO: Remove this null bit
    date = models.DateField(null=True)
    value = models.FloatField()


class ExchangeRate(models.Model):
    """
    Describes the rate from the first to the second currency
    """

    class Meta:
        unique_together = ("first", "second", "date")

    first = models.CharField(max_length=3)
    second = models.CharField(max_length=3)
    date = models.DateField()
    rate = models.FloatField()


class Supervisor(models.Model):
    user = models.OneToOneField(User, related_name="supervisor")
    firm = models.ForeignKey(Firm, related_name="supervisors")
    # has full authorization to make action in name of advisor and clients
    can_write = models.BooleanField(default=False,
                                    verbose_name="Has Full Access?",
                                    help_text="A supervisor with 'full access' can impersonate advisors and clients "
                                              "and make any action as them.")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        is_new_instance = False

        if self.pk is None:
            is_new_instance = True

        ret = super(Supervisor, self).save(force_insert, force_update, using, update_fields)

        if is_new_instance:
            self.send_confirmation_email()

        return ret

    def send_confirmation_email(self):
        account_type = self._meta.verbose_name

        subject = "BetaSmartz new {0} account confirmation".format(account_type)

        context = {
            'subject': subject,
            'account_type': account_type,
            'firm_name': self.firm.name
        }

        send_mail(
            subject,
            '',
            None,
            [self.user.email],
            html_message=render_to_string('email/new_supervisor.html', context))


class ProxyAssetClass(AssetClass):
    class Meta:
        proxy = True
        verbose_name_plural = "Asset classes"
        verbose_name = "Asset class"


class ProxyTicker(Ticker):
    class Meta:
        proxy = True
        verbose_name_plural = "Tickers"
        verbose_name = "Ticker"


class View(models.Model):
    q = models.FloatField()
    assets = models.TextField()
    portfolio_set = models.ForeignKey(PortfolioSet, related_name="views")
