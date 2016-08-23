import uuid
from itertools import chain

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.db.models import PROTECT
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import gettext as _

from main import constants
from main.abstract import NeedApprobation, NeedConfirmation, PersonalData
from main.models import AccountGroup, Goal, Platform
from .managers import ClientAccountQuerySet, ClientQuerySet


class Client(NeedApprobation, NeedConfirmation, PersonalData):
    WORTH_AFFLUENT = 'affluent'
    WORTH_HIGH = 'high'
    WORTH_VERY_HIGH = 'very-high'
    WORTH_ULTRA_HIGH = 'ultra-high'

    WORTH_CHOICES = (
        (WORTH_AFFLUENT, 'Mass affluent'),
        (WORTH_HIGH, 'High net worth'),
        (WORTH_VERY_HIGH, 'Ultra high net worth'),
        (WORTH_ULTRA_HIGH, 'Very high net worth'),
    )

    WORTH_RANGES = (
        (WORTH_AFFLUENT, 0, 100000),
        (WORTH_HIGH, 100000, 1000000),
        (WORTH_VERY_HIGH, 1000000, 10000000),
        (WORTH_ULTRA_HIGH, 10000000, 1000000000),
    )

    advisor = models.ForeignKey('main.Advisor',
        related_name='all_clients',
        on_delete=PROTECT)  # Must reassign clients before removing advisor
    secondary_advisors = models.ManyToManyField(
        'main.Advisor',
        related_name='secondary_clients',
        editable=False)
    create_date = models.DateTimeField(auto_now_add=True)
    client_agreement = models.FileField()

    user = models.OneToOneField('main.User', related_name='client')
    tax_file_number = models.CharField(max_length=9, null=True, blank=True)
    provide_tfn = models.IntegerField(verbose_name='Provide TFN?',
                                      choices=constants.TFN_CHOICES,
                                      default=constants.TFN_YES)

    associated_to_broker_dealer = models.BooleanField(
        verbose_name="Are employed by or associated with "
                     "a broker dealer?",
        default=False,
        choices=constants.YES_NO)
    ten_percent_insider = models.BooleanField(
        verbose_name="Are you a 10% shareholder, director, or"
                     " policy maker of a publicly traded company?",
        default=False,
        choices=constants.YES_NO)

    public_position_insider = models.BooleanField(
        verbose_name=_("Do you or a family member hold "
                     "a public office position?"),
        default=False,
        choices=constants.YES_NO)

    us_citizen = models.BooleanField(
        verbose_name="Are you a US citizen/person"
                     " for the purpose of US Federal Income Tax?",
        default=False,
        choices=constants.YES_NO)

    employment_status = models.IntegerField(choices=constants.EMPLOYMENT_STATUSES,
                                            null=True, blank=True)
    income = models.FloatField(verbose_name="Income ($)", default=0)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    employer = models.CharField(max_length=255, null=True, blank=True)
    betasmartz_agreement = models.BooleanField(default=False)
    advisor_agreement = models.BooleanField(default=False)
    last_action = models.DateTimeField(null=True)

    objects = ClientQuerySet.as_manager()

    def __str__(self):
        return self.user.get_full_name()

    def _net_worth(self):
        # Sum ExternalAssets for the client
        assets = self.external_assets.all()
        assets_worth = 0.0
        for a in assets:
            assets_worth += float(a.valuation)
        # Sum personal type Betasmartz Accounts - the total balance for the account is
        # ClientAccount.cash_balance + Goal.total_balance for all goals for the account.
        personal_accounts_worth = 0.0
        for ca in self.primary_accounts.filter(account_type=constants.ACCOUNT_TYPE_PERSONAL):
            personal_accounts_worth += ca.cash_balance
            for goal in ca.all_goals.exclude(state=Goal.State.ARCHIVED.value):
                personal_accounts_worth += goal.total_balance
        return assets_worth + personal_accounts_worth

    @property
    def net_worth(self):
        # is it ok to use a property here to cache a client's net worth?
        return self._net_worth()

    @property
    def accounts_all(self):
        # TODO: Make this work
        #return self.primary_accounts.get_queryset() | self.signatories.select_related('account')
        return self.primary_accounts

    @property
    def accounts(self):
        return self.accounts_all.filter(confirmed=True)

    def get_worth(self):
        # why it should be a property? it shouldn't
        total_balance = self.total_balance

        for worth_range in self.WORTH_RANGES:
            if total_balance >= worth_range[1] and total_balance < worth_range[2]:
                return worth_range[0]

    def get_worth_display(self):
        worth = dict(self.WORTH_CHOICES)
        return worth.get(self.get_worth())

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
        today = now().today()
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
            risk_profile_group = AccountTypeRiskProfileGroup.objects.all().filter(account_type=constants.ACCOUNT_TYPE_PERSONAL).first()
            if risk_profile_group is None:
                raise ValidationError("No risk profile group associated with account type: ACCOUNT_TYPE_PERSONAL")
            new_ac = ClientAccount(
                primary_owner=self,
                account_type=constants.ACCOUNT_TYPE_PERSONAL,
                default_portfolio_set=self.advisor.default_portfolio_set,
                risk_profile_group=risk_profile_group.risk_profile_group
            )
            new_ac.save()
            new_ac.remove_from_group()


class ClientAccount(models.Model):
    """
    A ClientAccount is not just for Personal accounts. It is our base account, from which other data can be attached.
    It is the primary financial entity in the Betasmartz system.
    """
    account_group = models.ForeignKey('main.AccountGroup',
                                      related_name="accounts_all",
                                      null=True)
    custom_fee = models.PositiveIntegerField(default=0)
    account_type = models.IntegerField(choices=constants.ACCOUNT_TYPES)
    account_name = models.CharField(max_length=255, default='PERSONAL')
    primary_owner = models.ForeignKey('Client', related_name="primary_accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=36, editable=False)
    confirmed = models.BooleanField(default=False)
    tax_loss_harvesting_consent = models.BooleanField(default=False)
    tax_loss_harvesting_status = models.CharField(max_length=255, choices=(("USER_OFF", "USER_OFF"),
                                                                           ("USER_ON", "USER_ON")), default="USER_OFF")
    asset_fee_plan = models.ForeignKey('main.AssetFeePlan', null=True)
    default_portfolio_set = models.ForeignKey('main.PortfolioSet')
    cash_balance = models.FloatField(default=0, help_text='The amount of cash in this account available to be used.')
    supervised = models.BooleanField(default=True, help_text='Is this account supervised by an advisor?')
    signatories = models.ManyToManyField('Client',
                                         related_name='signatory_accounts',
                                         help_text='Other clients authorised to operate the account.')
    risk_profile_group = models.ForeignKey('RiskProfileGroup', related_name='accounts')
    # The account must not be used until the risk_profile_responses are set.
    risk_profile_responses = models.ManyToManyField('RiskProfileAnswer')

    objects = ClientAccountQuerySet.as_manager()

    class Meta:
        unique_together = ('primary_owner', 'account_name')

    @property
    def goals(self):
        return self.all_goals.exclude(state=Goal.State.ARCHIVED.value)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.token = str(uuid.uuid4())

        return super(ClientAccount, self).save(force_insert, force_update,
                                               using, update_fields)

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

    @property
    def advisors(self):
        return chain([self.primary_owner.advisor, self.account_group.advisor],
                     self.account_group.secondary_advisors.all())

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
            return self.primary_owner.advisor.firm.fee + Platform.objects.first().fee

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
    def core_balance(self):
        b = 0
        for goal in self.goals.all():
            b += goal.core_balance
        return b

    @property
    def satellite_balance(self):
        b = 0
        for goal in self.goals.all():
            b += goal.satellite_balance
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
    def owners(self):
        return self.primary_owner.full_name

    @property
    def account_type_name(self):
        for at in constants.ACCOUNT_TYPES:
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

    def get_worth(self):
        total_balance = self.total_balance

        for worth_range in Client.WORTH_RANGES:
            if total_balance >= worth_range[1] and total_balance < worth_range[2]:
                return worth_range[0]

    def get_worth_display(self):
        worth = dict(Client.WORTH_CHOICES)
        return worth.get(self.get_worth())

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


class RiskProfileGroup(models.Model):
    """
    A way to group a set of predefined risk profile questions to be asked together.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    # Also has properties:
    #   'accounts' which is all the accounts this group is used on. From the ClientAccount model
    #   'questions' which is all the risk profile questions that form this group. From the RiskProfileQuestion model
    #   'account-types' which is all the account types where this group is the default group for the account type.

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class AccountTypeRiskProfileGroup(models.Model):
    account_type = models.IntegerField(choices=constants.ACCOUNT_TYPES, unique=True)
    risk_profile_group = models.ForeignKey('RiskProfileGroup', related_name='account_types')


class RiskProfileQuestion(models.Model):
    """
    The set of predefined risk profile questions.
    """
    group = models.ForeignKey('RiskProfileGroup', related_name='questions')
    order = models.IntegerField()
    text = models.TextField()

    # Also has property 'answers' which is all the predefined answers for this question.

    class Meta:
        ordering = ['order']
        unique_together = ('group', 'order')


class RiskProfileAnswer(models.Model):
    """
    The set of predefined answers to a risk profile question.
    """
    question = models.ForeignKey('RiskProfileQuestion', related_name='answers')
    order = models.IntegerField()
    text = models.TextField()
    score = models.FloatField()

    # Also has property 'responses' which is all the responses given that use this answer.

    class Meta:
        ordering = ['order']
        unique_together = ('question', 'order')


class EmailNotificationPrefs(models.Model):
    client = models.OneToOneField('Client', related_name='notification_prefs')
    auto_deposit = models.BooleanField(
        verbose_name=_('to remind me a day before my automatic '
                       'deposits will be transferred'),
        default=True)
    hit_10mln = models.BooleanField(
        verbose_name=_('when my account balance hits $10,000,000'),
        default=False)
