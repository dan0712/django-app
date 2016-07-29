import logging
import uuid
from datetime import datetime
from enum import Enum, unique
from itertools import repeat

import scipy.stats as st
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
    UserManager, send_mail)
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import (MaxValueValidator, MinLengthValidator,
    MinValueValidator, RegexValidator, ValidationError)
from django.db import models, transaction
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django_pandas.managers import DataFrameManager
from jsonfield.fields import JSONField
from phonenumber_field.modelfields import PhoneNumberField
from pinax.eventlog import models as el_models
from recurrence.base import deserialize

from address.models import Address
from common.structures import ChoiceEnum
from . import constants
from .abstract import (FinancialInstrument, NeedApprobation,
    NeedConfirmation, PersonalData, TransferPlan)
from .fields import ColorField
from .management.commands.build_returns import get_price_returns
from .managers import ExternalAssetQuerySet, GoalQuerySet, PositionQuerySet, \
    RetirementPlanQuerySet
from .slug import unique_slugify

logger = logging.getLogger('main.models')


class Section:
    def __init__(self, section, form):
        self.header = section.get("header", "")
        self.detail = section.get("detail", None)
        self.css_class = section.get("css_class", None)
        self.fields = []
        for field_name in section["fields"]:
            self.fields.append(form[field_name])


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
    middle_name = models.CharField(_('middle name(s)'), max_length=30,
                                   blank=True)
    last_name = models.CharField(_('last name'), max_length=30, db_index=True)
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

    date_joined = models.DateTimeField(_('date joined'), default=now)
    prepopulated = models.BooleanField(default=False)

    avatar = models.ImageField(_('avatar'), blank=True, null=True)

    # aka activity
    notifications = GenericRelation('notifications.Notification',
                                    related_query_name='users',
                                    content_type_field='actor_content_type_id',
                                    object_id_field='actor_object_id')

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

        return self._is_advisor

    @property
    def is_authorised_representative(self):
        """
        Custom helper method for User class to check user type/profile.
        """
        if not hasattr(self, '_is_authorised_representative'):
            ar = hasattr(self, 'authorised_representative')
            self._is_authorised_representative = ar

        return self._is_authorised_representative

    @property
    def is_client(self):
        """
        Custom helper method for User class to check user type/profile.
        """
        if not hasattr(self, '_is_client'):
            self._is_client = hasattr(self, 'client')

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

    def email_user(self, subject, message,
                   from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class AssetClass(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[0-9A-Z_]+$',
            message="Invalid character only accept (0-9a-zA-Z_) ")],
        unique=True)
    display_order = models.PositiveIntegerField(db_index=True)
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True, null=False,
                                               default='')
    tickers_explanation = models.TextField(blank=True, default='', null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False,
                                    db_index=True)
    # TODO: should be converted to Integer
    investment_type = models.CharField(max_length=255,
                                       choices=constants.INVESTMENT_TYPES,
                                       blank=False, null=False, db_index=True)
    # TODO: should be converted to Integer
    super_asset_class = models.CharField(max_length=255,
                                         choices=constants.SUPER_ASSET_CLASSES,
                                         db_index=True)

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


class ExternalAsset(models.Model):
    class Type(ChoiceEnum):
        FAMILY_HOME = (0, 'Family Home')
        INVESTMENT_PROPERTY = (1, 'Investment Property')
        INVESTMENT_PORTFOLIO = (2, 'Investment Portfolio')
        SAVINGS_ACCOUNT = (3, 'Savings Account')
        PROPERTY_LOAN = (4, 'Property Loan')
        TRANSACTION_ACCOUNT = (5, 'Transaction Account')
        RETIREMENT_ACCOUNT = (6, 'Retirement Account')
        OTHER = (7, 'Other')

    type = models.IntegerField(choices=Type.choices())
    name = models.CharField(max_length=128)
    owner = models.ForeignKey('client.Client', related_name='external_assets')
    description = models.TextField(blank=True, null=True)
    valuation = models.DecimalField(decimal_places=2,
                                    max_digits=15, # Up to 9.9... trillion
                                    help_text='In the system currency. Could be negative if a debt')
    valuation_date = models.DateField(help_text='Date when the asset was valued')
    growth = models.DecimalField(decimal_places=4,
                                 max_digits=5,
                                 help_text='Modeled annualized growth of the asset - pos or neg. 0.0 is no growth')
    acquisition_date = models.DateField(help_text="Could be in the future if it's a future acquisition")
    debt = models.OneToOneField('ExternalAsset',
                                related_name='for_asset',
                                help_text="Any debt that is directly associated to the asset.",
                                null=True,
                                on_delete=SET_NULL)
    # Also has a 'transfer_plan' field from ExternalAssetTransfer

    # Override the manager with one that has permission capabilities.
    objects = ExternalAssetQuerySet.as_manager()

    class Meta:
        unique_together = ('name', 'owner')


class ExternalAccount(ExternalAsset):
    institution = models.CharField(max_length=128, help_text='Institute where the account is held.')
    account_id = models.CharField(max_length=64)


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
        if application_type == constants.AUTHORIZED_REPRESENTATIVE:
            return self.authorised_representative_form_url
        if application_type == constants.INVITATION_ADVISOR:
            return self.advisor_invite_url
        if application_type == constants.INVITATION_SUPERVISOR:
            return self.supervisor_invite_url

    def __str__(self):
        return self.name


class FirmData(models.Model):
    class Meta:
        verbose_name = "Firm detail"

    firm = models.OneToOneField(Firm, related_name='firm_details')
    afsl_asic = models.CharField("AFSL/ASIC number", max_length=50)
    afsl_asic_document = models.FileField("AFSL/ASIC doc.")
    office_address = models.ForeignKey(Address, related_name='+')
    postal_address = models.ForeignKey(Address, related_name='+')

    daytime_phone_num = PhoneNumberField(max_length=16)  # A firm MUST have some number to contact them by.
    mobile_phone_num = PhoneNumberField(null=True, max_length=16)  # A firm may not have a mobile number as well.
    fax_num = PhoneNumberField(null=True, max_length=16)  # Not all businesses have a fax.

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
    work_phone_num = PhoneNumberField(null=True, max_length=16)
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
        all_households = (list(self.primary_account_groups.all()) +
                          list(self.secondary_account_groups.all()))
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
        return self.all_clients.filter(user__prepopulated=False).count()

    @property
    def secondary_clients_size(self):
        return (self.secondary_clients.filter(user__prepopulated=False)
                .distinct().count())

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


class AuthorisedRepresentative(NeedApprobation, NeedConfirmation, PersonalData):
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
    def core_balance(self):
        b = 0
        for account in self.accounts.all():
            b += account.core_balance
        return b

    @property
    def satellite_balance(self):
        b = 0
        for account in self.accounts.all():
            b += account.satellite_balance
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
    def core_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.core_balance / self.total_balance * 100)))

    @property
    def satellite_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(int(round(self.satellite_balance / self.total_balance * 100)))

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


class RetirementPlan(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey('client.Client')
    # Assigning a partner_plan gives anyone with permissions to modify the partner_plan authority to modify this plan.
    partner_plan = models.OneToOneField('RetirementPlan',
                                        related_name='partner_plan_reverse',
                                        null=True,
                                        on_delete=models.SET_NULL)
    begin_date = models.DateField(auto_now_add=True, help_text="Date the retirement plan is supposed to begin.")
    retirement_date = models.DateField()
    life_expectancy = models.IntegerField(help_text="Until what age do we want to plan retirement spending?")
    spendable_income = models.IntegerField(default=0, help_text="The current annual spendable income. This must be identical across partner plans as they have a common spendable income.")
    desired_income = models.IntegerField(default=0, help_text="The desired annual spendable income in retirement")
    # Each account can have at most one retirement plan. Hence the relationship goes this way.
    smsf_account = models.OneToOneField('client.ClientAccount',
                                        related_name='retirement_plan',
                                        help_text="The associated SMSF account.",
                                        null=True)
    # Also has fields btc, atc and external_income from related models.

    # Install the custom manager that knows how to filter.
    objects = RetirementPlanQuerySet.as_manager()

    class Meta:
        unique_together = ('name', 'client')

    def save(self, *args, **kwargs):
        """
        Override save() so we can do some custom validation of partner plans.
        """
        reverse_plan = getattr(self, 'partner_plan_reverse', None)
        if self.partner_plan is not None and reverse_plan is not None and self.partner_plan != reverse_plan:
            raise ValidationError("Partner plan relationship must be symmetric.")

        super(RetirementPlan, self).save(*args, **kwargs)


class ExternalAssetTransfer(TransferPlan):
    asset = models.OneToOneField(ExternalAsset, related_name='transfer_plan', on_delete=CASCADE)


class RetirementPlanBTC(TransferPlan):
    plan = models.OneToOneField(RetirementPlan, related_name='btc')


class RetirementPlanATC(TransferPlan):
    plan = models.OneToOneField(RetirementPlan, related_name='atc')


class RetirementPlanEinc(TransferPlan):
    plan = models.ForeignKey(RetirementPlan, related_name='external_income')


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
    benchmark_content_type = models.ForeignKey(ContentType,
                                               on_delete=models.CASCADE,
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
        return self.asset_class.investment_type == constants.STOCKS

    @property
    def is_core(self):
        # Experimental
        # TODO: it will be deadly slow. need to to change all core models asap
        core_feature_value = AssetFeatureValue.Standard.FUND_TYPE_CORE.get_object()
        return self.features.filter(pk=core_feature_value.pk).exists()

    @property
    def is_satellite(self):
        # Experimental
        # TODO: it will be deadly slow. need to to change all core models asap
        satellite_feature_value = AssetFeatureValue.Standard.FUND_TYPE_SATELLITE.get_object()
        return self.features.filter(pk=satellite_feature_value.pk).exists()

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
    status = models.PositiveIntegerField(choices=constants.EMAIL_INVITATION_STATUSES,
                                         default=constants.INVITATION_PENDING)
    invitation_type = models.PositiveIntegerField(
        choices=constants.INVITATION_TYPE_CHOICES,
        default=constants.INVITATION_CLIENT)

    @property
    def get_status_name(self):
        for i in constants.EMAIL_INVITATION_STATUSES:
            if self.status == i[0]:
                return i[1]

    @property
    def get_status(self):
        try:
            user = User.objects.get(email=self.email)
        except User.DoesNotExist:
            user = None

        if user.prepopulated:
            return constants.INVITATION_PENDING

        if user is not None:
            if not user.is_active:
                self.status = constants.INVITATION_CLOSED
                self.save()

            for it in constants.INVITATION_TYPE_CHOICES:
                if self.invitation_type == it[0]:
                    model = constants.INVITATION_TYPE_DICT[str(it[0])]
                    if hasattr(user, model):
                        # match advisor or firm
                        profile = getattr(user, model)
                        if (profile.firm == self.inviter_object) or \
                                (getattr(profile, 'advisor', None) == self.inviter_object):
                            if profile.is_confirmed:
                                self.status = constants.INVITATION_ACTIVE
                                self.save()
                            else:
                                self.status = constants.INVITATION_SUBMITTED
                                self.save()
        return self.status

    def send(self):

        if self.get_status != constants.INVITATION_PENDING:
            return

        application_type = ""

        for itc in constants.INVITATION_TYPE_CHOICES:
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


class Platform(models.Model):
    fee = models.PositiveIntegerField(default=0)
    portfolio_set = models.ForeignKey(PortfolioSet)
    api = models.CharField(max_length=20,
                           default=constants.YAHOO_API,
                           choices=constants.API_CHOICES)

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


class AssetFee(models.Model):
    name = models.CharField(max_length=127)
    plan = models.ForeignKey(AssetFeePlan)
    collector = models.ForeignKey(Company)
    asset = models.ForeignKey(Ticker)
    applied_per = models.IntegerField(choices=constants.ASSET_FEE_EVENTS)
    fixed_level_unit = models.IntegerField(choices=constants.ASSET_FEE_UNITS)
    fixed_level_type = models.IntegerField(choices=constants.ASSET_FEE_LEVEL_TYPES)
    fixed_levels = models.TextField(help_text=constants._asset_fee_ht)
    prop_level_unit = models.IntegerField(choices=constants.ASSET_FEE_UNITS)
    prop_apply_unit = models.IntegerField(choices=constants.ASSET_FEE_UNITS)
    prop_level_type = models.IntegerField(choices=constants.ASSET_FEE_LEVEL_TYPES)
    prop_levels = models.TextField(help_text=constants._asset_fee_ht)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class GoalType(models.Model):
    # OBSOLETED # see RISK_LEVEL for GoalMetric
    #RISK_LEVEL_PROTECTED = 0 # 0.0
    #RISK_LEVEL_SEMI_PROTECTED = 20 # 0.2
    #RISK_LEVEL_MODERATE = 40 # 0.4
    #RISK_LEVEL_SEMI_DYNAMIC = 60 # 0.6
    #RISK_LEVEL_DYNAMIC = 80 # 0.8

    #RISK_LEVELS = (
    #    (RISK_LEVEL_PROTECTED, 'Protected'),
    #    (RISK_LEVEL_SEMI_PROTECTED, 'Semi-protected'),
    #    (RISK_LEVEL_MODERATE, 'Moderate'),
    #    (RISK_LEVEL_SEMI_DYNAMIC, 'Semi-dynamic'),
    #    (RISK_LEVEL_DYNAMIC, 'Dynamic'),
    #)

    name = models.CharField(max_length=255, null=False, db_index=True)
    description = models.TextField(null=True, blank=True)
    default_term = models.IntegerField(null=False)
    group = models.CharField(max_length=255, null=True)
    risk_sensitivity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Default risk sensitivity for this goal type. "
            "0 = not sensitive, 10 = Very sensitive (No risk tolerated)"
    )
    order = models.IntegerField(default=0, help_text="The order of the type in the list.")
    risk_factor_weights = JSONField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)

    def __str__(self):
        result = u'%s' % (self.name)
        return result

    # OBSOLETED
    #@classmethod
    #def risk_level_range(cls, risk_level):
    #    risk_min = risk_level
    #    risk_max = min([r[0] for r in cls.RISK_LEVELS if r[0] > risk_min] or [100]) # 100% or 101%?
    #    return [risk_min, risk_max]


class RecurringTransaction(models.Model):
    # Note: Only settings that are active will have their recurring transactions processed.
    setting = models.ForeignKey('GoalSetting', related_name='recurring_transactions')
    # Note: https://www.npmjs.com/package/rrule and https://www.npmjs.com/package/rrecur for UI side of below
    recurrence = models.TextField()
    enabled = models.BooleanField(default=True)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_transaction(self):
        # doesn't seem to work but just in case make date to be naïve
        return self.recurrence.after(now().replace(tzinfo=None), inc=True)

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
            # rrule uses naive dates
            between = rrule.between(start.replace(tzinfo=None),
                                    end.replace(tzinfo=None))
            res.extend(zip(between, repeat(r.amount)))
        return res


class Portfolio(models.Model):
    setting = models.OneToOneField('GoalSetting', related_name='portfolio')
    stdev = models.FloatField()
    er = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    # Also has 'items' field from PortfolioItem

    def __str__(self):
        result = u'Portfolio #%s' % (self.id)
        return result


class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='items')
    asset = models.ForeignKey(Ticker)
    weight = models.FloatField()
    volatility = models.FloatField(help_text='variance of this asset at the time of creating this portfolio.')


class GoalSetting(models.Model):
    target = models.FloatField(default=0)
    completion = models.DateField(help_text='The scheduled completion date for the goal.')
    hedge_fx = models.BooleanField(help_text='Do we want to hedge foreign exposure?')
    # metric_group is a foreignkey rather than onetoone since a metric group can be used by more than one setting object
    metric_group = models.ForeignKey('GoalMetricGroup', related_name='settings')
    rebalance = models.BooleanField(default=True, help_text='Do we want to perform automated rebalancing?')
    # also may have a 'recurring_transactions' field from RecurringTransaction model.
    # also may have a 'portfolio' field from Portfolio model. May be null if no portfolio has been assigned yet.

    def __str__(self):
        result = u'Goal Settings #%s (%s)' % (self.id, self.portfolio)
        return result

    @property
    def goal(self):
        if hasattr(self, 'goal_selected'):
            return self.goal_selected
        if hasattr(self, 'goal_approved'):
            return self.goal_approved
        # Must be an active goal
        return self.goal_active


class GoalMetricGroup(models.Model):
    TYPE_CUSTOM = 0
    TYPE_PRESET = 1
    TYPES = (
        (TYPE_CUSTOM, 'Custom'),  # Should be deleted when it is not used by any settings object
        (TYPE_PRESET, 'Preset'),  # Exists on it's own.
    )
    type = models.IntegerField(choices=TYPES, default=TYPE_CUSTOM)
    name = models.CharField(max_length=100, null=True)
    # also has field 'metrics' from GoalMetric
    # Also has field 'settings' from GoalSetting

    def __str__(self):
        return "[{}:{}] {}".format(self.id, GoalMetricGroup.TYPES[self.type][1], self.name)

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

    account = models.ForeignKey('client.ClientAccount', related_name="all_goals")
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
    state = models.IntegerField(choices=State.choices(), default=State.ACTIVE.value)
    order = models.IntegerField(default=0, help_text="The desired position in the list of Goals")

    # Also has 'positions' field from Position model.

    objects = GoalQuerySet.as_manager()

    class Meta:
        ordering = ['order']
        unique_together = ('account', 'name')

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

        # Remove outstanding orders and close existing positions
        async_id = OrderManager.close_positions(self)

        self.state = self.State.ARCHIVED.value if async_id is None else self.State.CLOSING.value

        # Change the name to _ARCHIVED so it doesn't affect the way the client can name any new goals, as there is a
        # unique index on account and name
        self.name += '_ARCHIVED'
        names = Goal.objects.filter(account=self.account).exclude(id=self.id).values_list('name', flat=True)
        if self.name in names:
            suf = 1
            while '{}_{}'.format(self.name, suf) in names:
                suf += 1
            self.name += '_{}'.format(suf)

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
            custom_group = old_setting.metric_group.type == GoalMetricGroup.TYPE_CUSTOM
            last_user = old_setting.metric_group.settings.count() == 1
            if custom_group and last_user:
                # This will also delete the setting as the metric group is a foreign key.
                old_setting.metric_group.delete()
            else:
                # We are using a shared group, or we're not the last user. Just delete the setting object.
                old_setting.delete()

    @transaction.atomic
    def approve_selected(self):
        old_setting = self.approved_settings
        if self.selected_settings == old_setting:
            return
        self.approved_settings = self.selected_settings
        self.save()
        if old_setting != self.active_settings:
            old_setting.delete()

    @transaction.atomic
    def revert_selected(self):
        if self.approved_settings is None:
            raise ValidationError("There are no current approved settings. Cannot revert.")
        old_setting = self.selected_settings
        if self.approved_settings == old_setting:
            return
        self.selected_settings = self.approved_settings
        self.save()
        old_setting.delete()

    @property
    def available_balance(self):
        return self.total_balance - self.pending_outgoings

    @property
    def pending_transactions(self):
        return Transaction.objects.filter((Q(to_goal=self) | Q(from_goal=self)) & Q(status=Transaction.STATUS_PENDING))

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
                                            (Q(reason__in=Transaction.CASH_FLOW_REASONS))):
            inputs += t.amount if self == t.to_goal else -t.amount
        return inputs

    @property
    def net_executions(self):
        """
        :return: The net realised amount invested in funds(Sum Order type transactions)
        """
        inputs = 0.0
        for t in Transaction.objects.filter(Q(status=Transaction.STATUS_EXECUTED) &
                                            (Q(to_goal=self) | Q(from_goal=self)) &
                                            Q(reason=Transaction.REASON_EXECUTION)):
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

    @property
    def risk_level(self):
        # Experimental
        goal_metric = GoalMetric.objects \
            .filter(type=GoalMetric.METRIC_TYPE_RISK_SCORE) \
            .filter(group__settings__goal_approved=self) \
            .first()

        if goal_metric:
            risk_level = goal_metric.get_risk_level_display()
            return risk_level

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

        # use naïve dates for calculations
        current_time = now().replace(tzinfo=None)
        # Get the predicted cash-flow events until the provided future date
        cf_events = [(current_time, self.total_balance)]
        if hasattr(self.selected_settings, 'recurring_transactions'):
            cf_events += RecurringTransaction.get_events(self.selected_settings.recurring_transactions,
                                                         current_time,
                                                         datetime.combine(future_dt, now().timetz()))

        # TODO: Add estimated fee events to this.

        # Calculate the predicted_balance based on cash flow events, er, stdev and z_mult
        predicted = 0
        for dt, val in cf_events:
            tdelta = dt - current_time
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
    def core_balance(self):
        v = 0
        for p in self.positions.all():
            if p.is_core:
                v += p.value
        return v

    @property
    def satellite_balance(self):
        v = 0
        for p in self.positions.all():
            if p.is_satellite:
                v += p.value
        return v

    @property
    def total_return(self):
        """
        :return: The Time-Weighted Return for this goal
        """
        # TODO: Do it properly
        fund_bal = self.total_balance - self.cash_balance
        exec_total = self.net_executions
        return (fund_bal + exec_total) / -exec_total if exec_total else 0

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
        today = now().today()

        term = (self.selected_settings.completion.year - today.year
                if self.selected_settings else None)

        return term

    @property
    def auto_term(self):
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
    @unique
    class Standard(Enum):
        SRI = 0
        ASSET_TYPE = 1
        FUND_TYPE = 2
        REGION = 3
        ASSET_CLASS = 4
        CURRENCY = 5
        # TODO: Add the rest

        def get_object(self):
            names = {
                # feature_tag: feature_name
                self.SRI: 'Social Responsibility',
                self.ASSET_TYPE: 'Asset Type',
                self.FUND_TYPE: 'Fund Type',
                self.REGION: 'Region',
                self.ASSET_CLASS: 'Asset Class',
                self.CURRENCY: 'Currency',
                # TODO: Add the rest
            }
            return AssetFeature.objects.get_or_create(name=names[self])[0]

    name = models.CharField(max_length=127, unique=True, help_text="This should be a noun such as 'Region'.")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class AssetFeatureValue(models.Model):
    @unique
    class Standard(Enum):
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
                self.SRI_OTHER: (AssetFeature.Standard.SRI, 'Socially Responsible Investments'),
                self.ASSET_TYPE_STOCK: (AssetFeature.Standard.ASSET_TYPE, 'Stocks only'),
                self.ASSET_TYPE_BOND: (AssetFeature.Standard.ASSET_TYPE, 'Bonds only'),
                self.FUND_TYPE_CORE: (AssetFeature.Standard.FUND_TYPE, 'Core (ETFs)'),
                self.FUND_TYPE_SATELLITE: (AssetFeature.Standard.FUND_TYPE, 'Satellite (Actively Managed)'),
                self.REGION_AUSTRALIAN: (AssetFeature.Standard.REGION, 'Australian'),
            }
            return AssetFeatureValue.objects.get_or_create(name=data[self][1],
                                                           defaults={'feature': data[self][0].get_object()})[0]

    class Meta:
        unique_together = ('name', 'feature')

    name = models.CharField(max_length=127, help_text="This should be an adjective.")
    description = models.TextField(blank=True, null=True, help_text="A clarification of what this value means.")
    feature = models.ForeignKey(AssetFeature,
                                related_name='values',
                                on_delete=PROTECT,
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

    # Experimental
    RISK_LEVEL_PROTECTED = 0 # 0.0
    RISK_LEVEL_SEMI_PROTECTED = 20 # 0.2
    RISK_LEVEL_MODERATE = 40 # 0.4
    RISK_LEVEL_SEMI_DYNAMIC = 60 # 0.6
    RISK_LEVEL_DYNAMIC = 80 # 0.8

    RISK_LEVELS = (
        (RISK_LEVEL_PROTECTED, 'Protected'),
        (RISK_LEVEL_SEMI_PROTECTED, 'Semi-protected'),
        (RISK_LEVEL_MODERATE, 'Moderate'),
        (RISK_LEVEL_SEMI_DYNAMIC, 'Semi-dynamic'),
        (RISK_LEVEL_DYNAMIC, 'Dynamic'),
    )

    # OBSOLETED # setting = models.ForeignKey(GoalSetting, related_name='metrics', null=True)
    group = models.ForeignKey('GoalMetricGroup', related_name='metrics')
    type = models.IntegerField(choices=metric_types.items())
    feature = models.ForeignKey(AssetFeatureValue, null=True, on_delete=PROTECT)
    comparison = models.IntegerField(default=1, choices=comparisons.items())
    rebalance_type = models.IntegerField(choices=rebalance_types.items(),
                                         help_text='Is the rebalance threshold an absolute threshold or relative (percentage difference) threshold?')
    rebalance_thr = models.FloatField(
        help_text='The difference between configured and measured value at which a rebalance will be recommended.')
    configured_val = models.FloatField(help_text='The value of the metric that was configured.')
    measured_val = models.FloatField(help_text='The latest measured value of the metric', null=True)

    @classmethod
    def risk_level_range(cls, risk_level):
        risk_min = risk_level
        risk_max = min([r[0] for r in cls.RISK_LEVELS if r[0] > risk_min] or [100]) # 100% or 101%?
        return [risk_min, risk_max]

    def get_risk_level(self):
        for risk_level_choice in self.RISK_LEVELS:
            risk_min, risk_max = self.risk_level_range(risk_level_choice[0])

            if self.configured_val < risk_max / 100:
                return risk_min

    def get_risk_level_display(self):
        risk_level = self.get_risk_level()

        if risk_level is not None:
            return dict(self.RISK_LEVELS)[risk_level]

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

    objects = PositionQuerySet.as_manager()

    @property
    def is_stock(self):
        return self.ticker.is_stock

    @property
    def is_core(self):
        return self.ticker.is_core

    @property
    def is_satellite(self):
        return self.ticker.is_satellite

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
    account = models.ForeignKey('client.ClientAccount', related_name='market_orders', on_delete=PROTECT)
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

    def __str__(self):
        return '{}|{}|{}|{}@{}'.format(self.id, self.executed, self.asset, self.volume, self.price)


class ExecutionDistribution(models.Model):
    # One execution can contribute to many distributions.
    execution = models.ForeignKey('Execution', related_name='distributions', on_delete=PROTECT)
    transaction = models.OneToOneField('Transaction', related_name='execution_distribution', on_delete=PROTECT)
    volume = models.FloatField(help_text="The number of units from the execution that were applied to the transaction.")


class SymbolReturnHistory(models.Model):
    return_number = models.FloatField(default=0)
    symbol = models.CharField(max_length=20)
    date = models.DateField()


class Performer(models.Model):
    symbol = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    group = models.CharField(max_length=20,
                             choices=constants.PERFORMER_GROUP_CHOICE,
                             default=constants.PERFORMER_GROUP_BENCHMARK)
    allocation = models.FloatField(default=0)
    #portfolio_set = models.ForeignKey(PortfolioSet)
    portfolio_set = models.IntegerField()


class DailyPrice(models.Model):
    """
    If a Financial Instrument is tradable, it will have a price.
    """
    objects = DataFrameManager()

    class Meta:
        unique_together = ("instrument_content_type", "instrument_object_id", "date")

    # An instrument should be a subclass of financial instrument
    instrument_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    instrument_object_id = models.PositiveIntegerField(db_index=True)
    instrument = GenericForeignKey('instrument_content_type', 'instrument_object_id')
    date = models.DateField(db_index=True)
    price = models.FloatField(null=True)


class MarketCap(models.Model):
    """
    If a Financial Instrument is tradable, it will have a market capitalisation. This may not change often.
    """
    objects = DataFrameManager()

    class Meta:
        unique_together = ("instrument_content_type", "instrument_object_id", "date")

    # An instrument should be a subclass of financial instrument
    instrument_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    instrument_object_id = models.PositiveIntegerField()
    instrument = GenericForeignKey('instrument_content_type', 'instrument_object_id')
    date = models.DateField()
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
                                    help_text="A supervisor with 'full access' can perform actions for their advisers and clients.")

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


class Transaction(models.Model):
    """
    A transaction is a flow of funds to or from a goal.
    Deposits have a to_goal, withdrawals have a from_goal, transfers have both
    Every Transaction must have one or both.
    When one is null, it means it was to/from the account's cash.
    """
    # Import event here so we have it within our transaction.
    from main.event import Event

    STATUS_PENDING = 'PENDING'
    STATUS_EXECUTED = 'EXECUTED'
    STATUSES = (('PENDING', 'PENDING'), ('EXECUTED', 'EXECUTED'))

    REASON_DIVIDEND = 0 # TODO: don't use 0 for that, never (for very special values only)
    REASON_DEPOSIT = 1
    REASON_WITHDRAWAL = 2
    REASON_REBALANCE = 3
    REASON_TRANSFER = 4
    REASON_FEE = 5
    # Transaction is for a MarketOrderRequest. It's a transient transaction, for reserving funds. It will always be pending.
    # It will have it's amount reduced over time (converted to executions or rejections) until it's eventually removed.
    REASON_ORDER = 6
    # Transaction is for an Order Execution Distribution that occurred. Will always be in executed state.
    REASON_EXECUTION = 7
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

    # The list of events that are related to transaction executions
    EXECUTION_EVENTS = [
        Event.GOAL_DIVIDEND_DISTRIBUTION,
        Event.GOAL_DEPOSIT_EXECUTED,
        Event.GOAL_WITHDRAWAL_EXECUTED,
        Event.GOAL_REBALANCE_EXECUTED,
        Event.GOAL_TRANSFER_EXECUTED,
        Event.GOAL_FEE_LEVIED,
        Event.GOAL_ORDER_DISTRIBUTION,
    ]

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
    executed = models.DateTimeField(null=True, db_index=True)

    # May also have 'execution_request' field from the ExecutionRequest model if it has reason ORDER
    # May also have 'execution_distribution' field from the ExecutionDistribution model if it has reason EXECUTION

    def save(self, *args, **kwargs):
        if self.from_goal is None and self.to_goal is None:
            raise ValidationError("One or more of from_goal and to_goal is required")
        if self.from_goal == self.to_goal:
            raise ValidationError("Cannot transact with myself.")
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return '{}|{}|{}|{}|{}'.format(self.id, self.created, self.reason, self.status, self.amount)


class EventMemo(models.Model):
    event = models.ForeignKey(el_models.Log,
                              related_name="memos",
                              on_delete=PROTECT,  # We shouldn't be deleting event logs anyway.
                             )
    comment = models.TextField()
    staff = models.BooleanField(help_text="Staff memos can only be seen by staff members of the firm."
                                          " Non-Staff memos inherit the permissions of the logged event."
                                          " I.e. Whoever can see the event, can see the memo.")


class ActivityLog(models.Model):
    name = models.CharField(max_length=100, unique=True)
    format_str = models.TextField()
    format_args = models.TextField(null=True,
                                   blank=True,
                                   help_text="Dotted '.' dictionary path into the event 'extra' field for each arg "
                                             "in the format_str. Each arg path separated by newline."
                                             "Eg. 'request.amount'")
    # Also has field 'events' from ActivityLogEvent


class ActivityLogEvent(models.Model):
    # Import event here so we have it within our activitylogevent.
    from main.event import Event

    id = models.IntegerField(choices=Event.choices(), primary_key=True)
    # foreign key as one Activity Log formatter can cover multiple events.
    activity_log = models.ForeignKey(ActivityLog, related_name='events')

    @classmethod
    def get(cls, event: Event):
        # Import event here so we have it within our activitylogevent.
        from main.event import Event

        ale = cls.objects.filter(id=event.value).first()
        if ale is not None:
            return ale

        if event == Event.GOAL_DIVIDEND_DISTRIBUTION:
            alog = ActivityLog.objects.create(name='Dividend Transaction',
                                              format_str='Dividend payment of {{}}{} into goal'.format(settings.SYSTEM_CURRENCY),
                                              format_args='transaction.amount')
        elif event == Event.GOAL_DEPOSIT_EXECUTED:
            alog = ActivityLog.objects.create(name='Goal Deposit Transaction',
                                              format_str='Deposit of {{}}{} from Account to Goal'.format(settings.SYSTEM_CURRENCY),
                                              format_args='transaction.amount')
        elif event == Event.GOAL_WITHDRAWAL_EXECUTED:
            alog = ActivityLog.objects.create(name='Goal Withdrawal Transaction',
                                              format_str='Withdrawal of {{}}{} from Goal to Account'.format(settings.SYSTEM_CURRENCY),
                                              format_args='transaction.amount')
        elif event == Event.GOAL_REBALANCE_EXECUTED:
            alog = ActivityLog.objects.create(name='Goal Rebalance Transaction', format_str='Rebalance Applied')
        elif event == Event.GOAL_TRANSFER_EXECUTED:
            alog = ActivityLog.objects.create(name='Goal Transfer Transaction', format_str='Transfer Applied')
        elif event == Event.GOAL_FEE_LEVIED:
            alog = ActivityLog.objects.create(name='Goal Fee Transaction',
                                              format_str='Fee of {{}}{} applied'.format(settings.SYSTEM_CURRENCY),
                                              format_args='transaction.amount')
        elif event == Event.GOAL_ORDER_DISTRIBUTION:
            alog = ActivityLog.objects.create(name='Order Distribution Transaction', format_str='Order Distributed')
        elif event == Event.GOAL_BALANCE_CALCULATED:
            alog = ActivityLog.objects.create(name='Daily Balance', format_str='Daily Balance')
        else:
            alog = ActivityLog.objects.create(name=event.name, format_str='DEFAULT_TEXT: {}'.format(event.name))

        return ActivityLogEvent.objects.create(id=event.value, activity_log=alog)
