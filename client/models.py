import logging
import uuid
from itertools import chain
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
from django.db import models
from django.db.models import PROTECT
from django.db.models.aggregates import Min, Max, Sum
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.functional import cached_property
from jsonfield.fields import JSONField
from main import constants
from main.abstract import NeedApprobation, NeedConfirmation, PersonalData
from main.models import AccountGroup, Goal, Platform
from .managers import ClientAccountQuerySet, ClientQuerySet
from main.finance import mod_dietz_rate
from retiresmartz.models import RetirementAdvice, RetirementPlan
from pinax.eventlog.models import log
from retiresmartz import advice_responses
from main.event import Event
logger = logging.getLogger('client.models')


class Client(NeedApprobation, NeedConfirmation, PersonalData):
    WORTH_AFFLUENT = 'affluent'
    WORTH_HIGH = 'high'
    WORTH_VERY_HIGH = 'very-high'
    WORTH_ULTRA_HIGH = 'ultra-high'

    WORTH_CHOICES = (
        (WORTH_AFFLUENT, 'Mass affluent'),
        (WORTH_HIGH, 'High net worth'),
        (WORTH_VERY_HIGH, 'Very high net worth'),
        (WORTH_ULTRA_HIGH, 'Ultra high net worth'),
    )

    WORTH_RANGES = (
        (WORTH_AFFLUENT, 0, 100000),
        (WORTH_HIGH, 100000, 1000000),
        (WORTH_VERY_HIGH, 1000000, 10000000),
        (WORTH_ULTRA_HIGH, 10000000, 1000000000),
    )

    advisor = models.ForeignKey('main.Advisor',
                                related_name='all_clients',
                                # Must reassign clients before removing advisor
                                on_delete=PROTECT)
    secondary_advisors = models.ManyToManyField(
        'main.Advisor',
        related_name='secondary_clients',
        editable=False)
    create_date = models.DateTimeField(auto_now_add=True)
    client_agreement = models.FileField()

    user = models.OneToOneField('main.User', related_name='client')

    employment_status = models.IntegerField(choices=constants.EMPLOYMENT_STATUSES,
                                            null=True, blank=True)
    income = models.FloatField(verbose_name="Income ($)", default=0)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    employer = models.CharField(max_length=255, null=True, blank=True)
    smoker = models.NullBooleanField(null=True, blank=True)
    daily_exercise = models.PositiveIntegerField(null=True, blank=True,
                                                 help_text="In Minutes")
    weight = models.PositiveIntegerField(null=True, blank=True, help_text="In kilograms")
    height = models.PositiveIntegerField(null=True, blank=True, help_text="In centimeters")

    drinks = models.PositiveIntegerField(null=True, blank=True, help_text='Number of drinks per day')

    betasmartz_agreement = models.BooleanField(default=False)
    advisor_agreement = models.BooleanField(default=False)
    last_action = models.DateTimeField(null=True)
    risk_profile_group = models.ForeignKey('RiskProfileGroup', related_name='clients', null=True)
    risk_profile_responses = models.ManyToManyField('RiskProfileAnswer')
    other_income = models.IntegerField(null=True, blank=True)

    objects = ClientQuerySet.as_manager()

    def __str__(self):
        return self.user.get_full_name()

    def _net_worth(self):
        # Sum ExternalAssets for the client
        assets = self.external_assets.all()
        assets_worth = 0.0
        today = datetime.now().date()
        for a in assets:
            # daily growth not annual
            assets_worth += float(a.get_growth_valuation(to_date=today))
        # Sum personal type Betasmartz Accounts - the total balance for the account is
        # ClientAccount.cash_balance + Goal.total_balance for all goals for the account.
        personal_accounts_worth = 0.0
        for ca in self.primary_accounts.filter(account_type=constants.ACCOUNT_TYPE_PERSONAL):
            personal_accounts_worth += ca.cash_balance
            for goal in ca.all_goals.exclude(state=Goal.State.ARCHIVED.value):
                personal_accounts_worth += goal.total_balance
        return assets_worth + personal_accounts_worth

    @cached_property
    def net_worth(self):
        return self._net_worth()

    @property
    def accounts_all(self):
        # TODO: Make this work
        # return self.primary_accounts.get_queryset() |
        # self.signatories.select_related('account')
        return self.primary_accounts

    @property
    def accounts(self):
        return self.accounts_all.filter(confirmed=True)

    def get_worth(self):
        # why it should be a property? it shouldn't
        total_balance = self.total_balance

        for worth_range in self.WORTH_RANGES:
            if worth_range[1] <= total_balance < worth_range[2]:
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
    def total_balance(self):
        return sum(account.total_balance for account in self.accounts.all())

    @property
    def stocks_percentage(self):
        return 0

    @property
    def bonds_percentage(self):
        return 0

    @property
    def total_returns(self):
        return 0

    @property
    def total_earnings(self):
        return sum(a.total_earnings for a in self.accounts)

    @property
    def current_risk_profile_responses(self):
        """
         Get the answers for the current risk profile questions and ensure they
         are recent and valid, otherwise returns None
         :return: A valid RiskProfileAnswer queryset, or None if questions changed
        """
        if not hasattr(self.risk_profile_group, 'questions'):
            # No risk questions assigned, so we can't say anything about their willingness to take risk.
            return None
        qids = set(self.risk_profile_group.questions.all().values_list('id', flat=True))
        if len(qids) == 0:
            # No risk questions assigned, so we can't say anything about their willingness to take risk.
            return None

        aqs = self.risk_profile_responses.all()
        if not self.risk_profile_responses:
            # No risk responses given, so we can't say anything about their willingness to take risk.
            return None

        if not qids == set(aqs.values_list('question_id', flat=True)):
            # Risk responses are not complete, so we can't say anything about their willingness to take risk.
            return None

        return aqs

    @cached_property
    def on_track(self):
        """
            If any of client's accounts are off track,
            return False.  If all accounts are
            on track, return True.
        """
        for account in self.accounts:
            if not account.on_track:
                return False
        return True

    @property
    def life_expectancy(self):
        # TODO: Return a better extimate of life expectancy
        return 85

    def get_risk_profile_bas_scores(self):
        """
        Get the scores for an entity's willingness to take risk, based on a previous elicitation of its preferences.
        :return: Tuple of floats [0-1] (b_score, a_score, s_score)
        """
        answers = self.current_risk_profile_responses
        if not answers:
            return None

        scores = (answers.values('b_score', 'a_score', 's_score').aggregate(b_score=Sum('b_score'),
                                                                            a_score=Sum('a_score'),
                                                                            s_score=Sum('s_score')))

        extents = (
            RiskProfileAnswer.objects.filter(question__group=self.risk_profile_group)
            .values('question').annotate(
                min_b=Min('b_score'), max_b=Max('b_score'),
                min_a=Min('a_score'), max_a=Max('a_score'),
                min_s=Min('s_score'), max_s=Max('s_score'),
            ).aggregate(
                min_b_sum=Sum('min_b'), max_b_sum=Sum('max_b'),
                min_a_sum=Sum('min_a'), max_a_sum=Sum('max_a'),
                min_s_sum=Sum('min_s'), max_s_sum=Sum('max_s'),
            )
        )

        max_b = extents['max_b_sum']
        max_a = extents['max_a_sum']
        max_s = extents['max_s_sum']
        return (
            scores['b_score'] / max_b if max_b > 0 else 0,
            scores['a_score'] / max_a if max_a > 0 else 0,
            scores['s_score'] / max_s if max_s > 0 else 0,
        )


class IBAccount(models.Model):
    '''
    Specification of Interactive Brokers Account
    '''
    ib_account = models.CharField(max_length=32)
    bs_account = models.OneToOneField('ClientAccount', related_name='ib_account')


class ClientAccount(models.Model):
    """
    A ClientAccount is not just for Personal accounts. It is our base account,
    from which other data can be attached.
    It is the primary financial entity in the Betasmartz system.
    """
    account_group = models.ForeignKey('main.AccountGroup',
                                      related_name="accounts_all",
                                      null=True)
    custom_fee = models.PositiveIntegerField(default=0)
    account_type = models.IntegerField(choices=constants.ACCOUNT_TYPES)
    account_name = models.CharField(max_length=255, default='PERSONAL')
    primary_owner = models.ForeignKey('Client',
                                      related_name="primary_accounts")
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=36, editable=False)
    # The confirmed field indicates the account is fully ready to be used by the client.
    # The ClientAccount should be responsible for checking and setting the confirmed filed through
    # an as yet undefined set_confirmed() method.
    confirmed = models.BooleanField(default=False)
    tax_loss_harvesting_consent = models.BooleanField(default=False)
    tax_loss_harvesting_status = models.CharField(max_length=255, choices=(
        ("USER_OFF", "USER_OFF"),
        ("USER_ON", "USER_ON")), default="USER_OFF")
    asset_fee_plan = models.ForeignKey('main.AssetFeePlan', null=True)
    default_portfolio_set = models.ForeignKey('main.PortfolioSet')
    cash_balance = models.FloatField(default=0,
                                     help_text='The amount of cash in this '
                                               'account available to be used.')
    supervised = models.BooleanField(default=True,
                                     help_text='Is this account supervised '
                                               'by an advisor?')
    signatories = models.ManyToManyField('Client',
                                         related_name='signatory_accounts',
                                         help_text='Other clients authorised '
                                                   'to operate the account.',
                                         blank=True)
    # also has ib_account foreign key to IBAccount

    objects = ClientAccountQuerySet.as_manager()

    class Meta:
        unique_together = ('primary_owner', 'account_name')

    def __init__(self, *args, **kwargs):
        super(ClientAccount, self).__init__(*args, **kwargs)
        self.__was_confirmed = self.confirmed

    @property
    def goals(self):
        return self.all_goals.exclude(state=Goal.State.ARCHIVED.value)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.token = str(uuid.uuid4())
        if self.confirmed != self.__was_confirmed:
            self.on_confirmed_modified()
        ret_value = super(ClientAccount, self).save(force_insert, force_update, using, update_fields)
        self.__was_confirmed = self.confirmed
        return ret_value

    def on_confirmed_modified(self):
        from client.models import EmailInvite
        try:
            invitation = self.primary_owner.user.invitation
        except EmailInvite.DoesNotExist: invitation = None

        if invitation \
                and invitation.status != EmailInvite.STATUS_COMPLETE \
                and invitation.reason == EmailInvite.REASON_PERSONAL_INVESTING:
            invitation.onboarding_data = None
            invitation.status = EmailInvite.STATUS_COMPLETE
            invitation.save()

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
        platform = Platform.objects.first()
        if platform:
            platform_fee = platform.fee
        else:
            platform_fee = 0
        if self.custom_fee != 0:
            return self.custom_fee + platform_fee
        else:
            return self.primary_owner.advisor.firm.fee + \
                   platform_fee

    @property
    def fee_fraction(self):
        return self.fee / 1000

    @property
    def name(self):
        """if self.account_name == PERSONAL_ACCOUNT:
            return "{0}'s Personal Account".format(
                self.primary_owner.user.first_name)"""

        return "{0}'s {1}".format(self.primary_owner.user.first_name,
                                  self.account_name.title())

    @property
    def total_balance(self):
        balance = sum(goal.total_balance for goal in self.goals.all())
        return balance + self.cash_balance

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
    def average_return(self):
        return mod_dietz_rate(self.goals)

    @property
    def total_earnings(self):
        return sum(g.total_earnings for g in self.goals)

    @property
    def stocks_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(
            int(round(self.stock_balance / self.total_balance * 100)))

    @property
    def bonds_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(
            int(round(self.bond_balance / self.total_balance * 100)))

    @property
    def core_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(
            int(round(self.core_balance / self.total_balance * 100)))

    @property
    def satellite_percentage(self):
        if self.total_balance == 0:
            return 0
        return "{0}".format(
            int(round(self.satellite_balance / self.total_balance * 100)))

    @property
    def owners(self):
        return self.primary_owner.full_name

    @property
    def account_type_name(self):
        return constants.ACCOUNT_TYPES[self.account_type][1]

    @cached_property
    def on_track(self):
        """
            If any of client's goals are off track,
            return False.  If all goals are
            on track, return True.
        """
        for goal in self.goals:
            if not goal.on_track:
                return False
        return True

    @property
    def goals_length(self):
        return len(self.goals.all())

    def get_worth(self):
        total_balance = self.total_balance

        for worth_range in Client.WORTH_RANGES:
            if worth_range[1] <= total_balance < worth_range[2]:
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
        return settings.SITE_URL + "/client/confirm/account/{0}".format(
            self.pk)

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
                  html_message=render_to_string(
                      'email/confirm_new_client_account.html', context))

    def __str__(self):
        return "{0}:{1}:{2}:({3})".format(
            self.primary_owner.full_name,
            self.primary_owner.advisor.first_name,
            self.primary_owner.advisor.firm.name,
            self.account_type_name)


class RiskProfileGroup(models.Model):
    """
    A way to group a set of predefined risk profile questions to
    be asked together.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    # Also has properties:
    #   'accounts' which is all the accounts this group is used on.
    # From the ClientAccount model 'questions' which is all the risk profile
    # questions that form this group. From the RiskProfileQuestion model
    #   'account-types' which is all the account types where this group is
    # the default group for the account type.

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class AccountTypeRiskProfileGroup(models.Model):
    account_type = models.IntegerField(choices=constants.ACCOUNT_TYPES,
                                       unique=True)
    risk_profile_group = models.ForeignKey('RiskProfileGroup',
                                           related_name='account_types')


class RiskProfileQuestion(models.Model):
    """
    The set of predefined risk profile questions.
    """
    group = models.ForeignKey('RiskProfileGroup', related_name='questions')
    order = models.IntegerField()
    text = models.TextField()
    explanation = models.TextField()
    image = models.ImageField(_('question_image'), blank=True, null=True)

    # Also has property 'answers' which is all the predefined answers for
    # this question.

    class Meta:
        ordering = ['order']
        unique_together = ('group', 'order')

    def __str__(self):
        return self.text


class RiskProfileAnswer(models.Model):
    """
    The set of predefined answers to a risk profile question.
    """
    question = models.ForeignKey('RiskProfileQuestion', related_name='answers')
    order = models.IntegerField()
    text = models.TextField()
    image = models.ImageField(_('answer_image'), blank=True, null=True)
    b_score = models.FloatField(help_text="Indication of Behaviour towards risk. "
                                          "Higher means higher risk is idealogically acceptable.")
    a_score = models.FloatField(help_text="Indication of Ability to take risk. "
                                          "Higher means losses due to risk has less critical impact on the investor")
    s_score = models.FloatField(help_text="Indication of Investor sophistication. "
                                          "Higher means investor understands risk and investment matters.")

    # Also has property 'responses' which is all the responses given
    # that use this answer.

    class Meta:
        ordering = ['order']
        unique_together = ('question', 'order')

    def __str__(self):
        return self.text


class EmailNotificationPrefs(models.Model):
    client = models.OneToOneField('Client', related_name='notification_prefs')
    auto_deposit = models.BooleanField(
        verbose_name=_('to remind me a day before my automatic '
                       'deposits will be transferred'),
        default=True)
    hit_10mln = models.BooleanField(
        verbose_name=_('when my account balance hits $10,000,000'),
        default=False)


def generate_token():
    secret = str(uuid.uuid4()) + str(uuid.uuid4())
    return secret.replace('-', '')[:64]


class EmailInvite(models.Model):
    STATUS_CREATED = 0
    STATUS_SENT = 1
    STATUS_ACCEPTED = 2
    STATUS_EXPIRED = 3
    STATUS_COMPLETE = 4
    STATUSES = (
        (STATUS_CREATED, 'Created'),
        (STATUS_SENT, 'Sent'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_COMPLETE, 'Complete')
    )
    REASON_RETIREMENT = 1
    REASON_PERSONAL_INVESTING = 2
    REASONS = (
        (REASON_RETIREMENT, 'Retirement'),
        (REASON_PERSONAL_INVESTING, 'Personal Investing'),
    )

    advisor = models.ForeignKey('main.Advisor', related_name='invites')

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    user = models.OneToOneField('main.User', related_name='invitation',
                                null=True, blank=True)

    invite_key = models.CharField(max_length=64,
                                  default=generate_token)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    last_sent_at = models.DateTimeField(blank=True, null=True)
    send_count = models.PositiveIntegerField(default=0)

    reason = models.PositiveIntegerField(choices=REASONS,
                                         blank=True, null=True)
    status = models.PositiveIntegerField(choices=STATUSES,
                                         default=STATUS_CREATED)

    onboarding_data = JSONField(null=True, blank=True)
    tax_transcript = models.FileField(null=True, blank=True)

    def __str__(self):
        return '{} {} {} ({})'.format(self.first_name, self.middle_name[:1],
                                      self.last_name, self.email)

    @property
    def can_resend(self):
        return self.status in [self.STATUS_CREATED, self.STATUS_SENT, self.STATUS_ACCEPTED]

    def send(self):
        if not self.can_resend:
            raise ValidationError('Can be resend only in status '
                                  'CREATED or SENT')

        subject = "BetaSmartz client sign up form url"

        context = {
            'invite_url': self.advisor.get_invite_url('client', self.email),
            'advisor': self.advisor,
        }

        html_message = render_to_string('advisor/clients/invites/email.html',
                                        context)
        send_mail(subject, '', None, [self.email], html_message=html_message)
        self.last_sent_at = now()
        self.status = self.STATUS_SENT
        self.send_count += 1

        self.save(update_fields=['last_sent_at', 'send_count', 'status'])

    class Meta:
        # shouldn't have multiple EmailInvites from same advisor to same email address
        unique_together = ('advisor', 'email')


class RiskCategory(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False, unique=True)
    upper_bound = models.FloatField(validators=[MinValueValidator(0),
                                                MaxValueValidator(1)])

    class Meta:
        ordering = ['upper_bound']
        verbose_name = 'Risk Category'
        verbose_name_plural = 'Risk Categories'

    def __str__(self):
        return '[<{}] {}'.format(self.upper_bound, self.name)
