from __future__ import unicode_literals

import logging

from django.core.validators import MaxLengthValidator, MaxValueValidator, \
    MinLengthValidator, MinValueValidator, ValidationError
from django.db import models, transaction
from django.db.models.deletion import PROTECT, CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from jsonfield.fields import JSONField
from pinax.eventlog.models import Log

from common.structures import ChoiceEnum
from main.event import Event
from main.models import TransferPlan, GoalSetting, GoalMetricGroup
from main.risk_profiler import GoalSettingRiskProfile
from retiresmartz.managers import RetirementAdviceQueryset
from .managers import RetirementPlanQuerySet
from main import constants
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pinax.eventlog.models import log
from retiresmartz import advice_responses
from django.utils.functional import cached_property
import json
logger = logging.getLogger('retiresmartz.models')


class RetirementPlan(models.Model):
    class LifestyleCategory(ChoiceEnum):
        OK = 1, 'Doing OK'
        COMFORTABLE = 2, 'Comfortable'
        WELL = 3, 'Doing Well'
        LUXURY = 4, 'Luxury'

    class ExpenseCategory(ChoiceEnum):
        SHELTER = 1, 'Housing - Shelter'
        UTILS = 2, 'Housing - Utilities & Bills'
        TRANSPORTATION = 3, 'Transportation'
        VOLUNTARY_INSURANCE = 4, 'Voluntary Insurance'
        TUITION = 5, 'Tuition'
        OTHER = 6, 'Other'

    class SavingCategory(ChoiceEnum):
        HEALTH_GAP = 1, 'Health Gap'
        EMPLOYER_CONTRIBUTION = 2, 'Employer Retirement Contributions'
        TAXABLE_PRC = 3, 'Taxable Personal Retirement Contributions'
        TAX_PAID_PRC = 4, 'Tax-paid Personal Retirement Contributions'
        PERSONAL = 5, 'Personal'
        INHERITANCE = 6, 'Inheritance'

    class HomeStyle(ChoiceEnum):
        SINGLE_DETACHED = 1, 'Single, Detached'
        SINGLE_ATTACHED = 2, 'Single, Attached'
        MULTI_9_OR_LESS = 3, 'Multi-Unit, 9 or less'
        MULTI_10_TO_20 = 4, 'Multi-Unit, 10 - 20'
        MULTI_20_PLUS = 5, 'Multi-Unit, 20+'
        MOBILE_HOME = 6, 'Mobile Home'
        RV = 7, 'RV, Van, Boat, etc'

    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey('client.Client')

    partner_plan = models.OneToOneField('RetirementPlan',
                                        related_name='partner_plan_reverse',
                                        null=True,
                                        on_delete=models.SET_NULL)

    lifestyle = models.PositiveIntegerField(choices=LifestyleCategory.choices(),
                                            default=1,
                                            help_text="The desired retirement lifestyle")

    desired_income = models.PositiveIntegerField(
        help_text="The desired annual household pre-tax retirement income in system currency")
    income = models.PositiveIntegerField(
        help_text="The current annual personal pre-tax income at the start of your plan")

    volunteer_days = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        help_text="The number of volunteer work days selected")

    paid_days = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        help_text="The number of paid work days selected")

    same_home = models.BooleanField(
        help_text="Will you be retiring in the same home?")

    same_location = models.NullBooleanField(
        help_text="Will you be retiring in the same general location?",
        blank=True, null=True)

    retirement_postal_code = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(5), MaxLengthValidator(10)],
        help_text="What postal code will you retire in?")

    reverse_mortgage = models.BooleanField(
        help_text="Would you consider a reverse mortgage? (optional)")

    retirement_home_style = models.PositiveIntegerField(
        choices=HomeStyle.choices(), null=True, blank=True,
        help_text="The style of your retirement home")

    retirement_home_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The price of your future retirement home (in today's dollars)")

    beta_partner = models.BooleanField(
        default=False,
        help_text="Will BetaSmartz manage your partner's "
                  "retirement assets as well?")

    expenses = JSONField(
        null=True,
        blank=True,
        help_text="List of expenses [{id, desc, cat, who, amt},...]")
    savings = JSONField(null=True,
                        blank=True,
                        help_text="List of savings [{id, desc, cat, who, amt},...]")
    initial_deposits = JSONField(null=True,
                                 blank=True,
                                 help_text="List of deposits [{id, asset, goal, amt},...]")

    income_growth = models.FloatField(default=0,
                                      help_text="Above consumer price index (inflation)")
    expected_return_confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)],
                                                   help_text="Planned confidence of the portfolio returns given the "
                                                             "volatility and risk predictions.")

    retirement_age = models.PositiveIntegerField()

    btc = models.PositiveIntegerField(help_text="Annual personal before-tax "
                                                "contributions",
                                                blank=True)
    atc = models.PositiveIntegerField(help_text="Annual personal after-tax "
                                                "contributions",
                                                blank=True)

    max_employer_match_percent = models.FloatField(
        null=True, blank=True,
        help_text="The percent the employer matches of before-tax contributions"
    )

    desired_risk = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The selected risk appetite for this retirement plan")

    # This is a field, not calculated, so we have a historical record of the value.
    recommended_risk = models.FloatField(
        editable=False, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The calculated recommended risk for this retirement plan")

    # This is a field, not calculated, so we have a historical record of the value.
    max_risk = models.FloatField(
        editable=False, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The maximum allowable risk appetite for this retirement "
                  "plan, based on our risk model")

    # calculated_life_expectancy should be calculated,
    # read-only don't let client create/update
    calculated_life_expectancy = models.PositiveIntegerField(editable=False, blank=True)
    selected_life_expectancy = models.PositiveIntegerField()

    agreed_on = models.DateTimeField(null=True, blank=True)

    goal_setting = models.OneToOneField(GoalSetting, null=True, related_name='retirement_plan', on_delete=PROTECT)
    partner_data = JSONField(null=True, blank=True)

    # Install the custom manager that knows how to filter.
    objects = RetirementPlanQuerySet.as_manager()

    class Meta:
        unique_together = ('name', 'client')

    def __init__(self, *args, **kwargs):
        # Keep a copy of agreed_on so we can see if it's changed
        super(RetirementPlan, self).__init__(*args, **kwargs)
        self.__was_agreed = self.agreed_on

    def __str__(self):
        return "RetirementPlan {}".format(self.id)

    @property
    def was_agreed(self):
        return self.__was_agreed

    @transaction.atomic
    def set_settings(self, new_setting):
        """
        Updates the retirement plan with the new settings, and saves the plan
        :param new_setting: The new setting to set.
        :return:
        """
        old_setting = self.goal_setting
        self.goal_setting = new_setting
        self.save()
        if old_setting is not None:
            old_group = old_setting.metric_group
            custom_group = old_group.type == GoalMetricGroup.TYPE_CUSTOM
            last_user = old_group.settings.count() == 1
            old_setting.delete()
            if custom_group and last_user:
                old_group.delete()

    @cached_property
    def spendable_income(self):
        if isinstance(self.savings, str):
            savings = json.loads(self.savings)
        else:
            savings = self.savings

        if isinstance(self.expenses, str):
            expenses = json.loads(self.expenses)
        else:
            expenses = self.expenses

        if self.savings:
            savings_cost = sum([s.get('amt', 0) for s in savings])
        else:
            savings_cost = 0
        if self.expenses:
            expenses_cost = sum([e.get('amt', 0) for e in expenses])
        else:
            expenses_cost = 0
        return self.income - savings_cost - expenses_cost

    def save(self, *args, **kwargs):
        """
        Override save() so we can do some custom validation of partner plans.
        """
        self.calculated_life_expectancy = self.client.life_expectancy
        bas_scores = self.client.get_risk_profile_bas_scores()
        self.recommended_risk = GoalSettingRiskProfile._recommend_risk(bas_scores)
        self.max_risk = GoalSettingRiskProfile._max_risk(bas_scores)

        if self.was_agreed:
            raise ValidationError("Cannot save a RetirementPlan that has been agreed upon")

        reverse_plan = getattr(self, 'partner_plan_reverse', None)
        if self.partner_plan is not None and reverse_plan is not None and \
           self.partner_plan != reverse_plan:
            raise ValidationError(
                "Partner plan relationship must be symmetric."
            )

        if self.pk:
            # RetirementPlan is being created
            # default btc if btc not provided
            # SPEND = plan.spendable_income # available spending money 
            # CONTR = # contributions needed to reach their goal - not function for this yet
            # CONTC = validated_data['income'] * validated_data.get('max_employer_match_percent') # current retirement contributions
            if not self.btc:
                # user did not provide their own btc
                max_contributions = determine_accounts(self)
                if self.max_employer_match_percent:
                    income_btc = self.income * self.max_employer_match_percent
                else:
                    income_btc = self.income * 0.04
                self.btc = min(income_btc, max_contributions[0][1])

        super(RetirementPlan, self).save(*args, **kwargs)

        if self.get_soa() is None and self.id is not None:
            self.generate_soa()

    def get_soa(self):
        from statements.models import RetirementStatementOfAdvice
        qs = RetirementStatementOfAdvice.objects.filter(
            retirement_plan_id=self.pk
        )
        if qs.count():
            self.statement_of_advice = qs[0]
            return qs[0]
        else:
            return self.generate_soa()

    def generate_soa(self):
        from statements.models import RetirementStatementOfAdvice
        soa = RetirementStatementOfAdvice(retirement_plan_id=self.id)
        soa.save()
        return soa

    @property
    def portfolio(self):
        return self.goal_setting.portfolio if self.goal_setting else None

    @cached_property
    def on_track(self):
        if hasattr(self, '_on_track'):
            return self._on_track
        self._on_track = False
        return self._on_track

    @property
    def opening_tax_deferred_balance(self):
        # TODO: Sum the complete amount that is expected to be in the retirement plan accounts on account opening.
        return 0

    @property
    def opening_tax_paid_balance(self):
        # TODO: Sum the complete amount that is expected to be in the retirement plan accounts on account opening.
        return 0


@receiver(post_save, sender=RetirementPlan)
def resolve_retirement_invitations(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    from client.models import EmailInvite
    try:
        invitation = instance.client.user.invitation
    except EmailInvite.DoesNotExist:
        invitation = None
    if created and invitation \
            and invitation.status != EmailInvite.STATUS_COMPLETE \
            and invitation.reason == EmailInvite.REASON_RETIREMENT:
        invitation.onboarding_data = None
        invitation.tax_transcript = None
        invitation.status = EmailInvite.STATUS_COMPLETE
        invitation.save()


class RetirementPlanEinc(TransferPlan):
    name = models.CharField(max_length=128)
    plan = models.ForeignKey(RetirementPlan, related_name='external_income')


class RetirementSpendingGoal(models.Model):
    plan = models.ForeignKey(RetirementPlan, related_name='retirement_goals')
    goal = models.OneToOneField('main.Goal', related_name='retirement_plan')


class RetirementPlanAccount(models.Model):
    """
    TODO: Comment what this is.
    """
    plan = models.ForeignKey(RetirementPlan, related_name='retiree')
    account = models.OneToOneField('client.ClientAccount', related_name='retirement')

    def __str__(self):
        return "%s Plan %s Account %s" % (self.id, self.plan, self.account)


class RetirementLifestyle(models.Model):
    cost = models.PositiveIntegerField(
        help_text="The minimum expected cost in system currency of this "
                  "lifestyle in today's dollars"
    )
    holidays = models.TextField(help_text="The text for the holidays block")
    eating_out = models.TextField(
        help_text="The text for the eating out block"
    )
    health = models.TextField(help_text="The text for the health block")
    interests = models.TextField(help_text="The text for the interests block")
    leisure = models.TextField(help_text="The text for the leisure block")
    default_volunteer_days = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        help_text="The default number of volunteer work days selected "
                  "for this lifestyle"
    )

    default_paid_days = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        help_text="The default number of paid work days selected "
                  "for this lifestyle"
    )

    def __str__(self):
        return "RetirementLifestyle {}".format(self.id)


class RetirementAdvice(models.Model):
    plan = models.ForeignKey(RetirementPlan, related_name='advice', on_delete=CASCADE)
    trigger = models.ForeignKey(Log, related_name='advice', on_delete=PROTECT)
    dt = models.DateTimeField(auto_now_add=True)
    read = models.DateTimeField(blank=True, null=True)
    text = models.CharField(max_length=512)
    action = models.CharField(max_length=12, blank=True)
    action_url = models.CharField(max_length=512, blank=True)
    action_data = models.CharField(max_length=512, blank=True)

    objects = RetirementAdviceQueryset.as_manager()

    def save(self, *args, **kwargs):
        if self.action and not self.action_url:
            # make sure action_url is set if the action is
            raise ValidationError('must provide action_url if action is set')
        super(RetirementAdvice, self).save(*args, **kwargs)

    def __str__(self):
        return "{} Advice {}".format(self.plan, self.id)


def determine_accounts(plan):
    """
    Generates a list of (account_type, max_contribution)
    in order of contribution priority where the account
    to put max contributions in first is first.
    """
    # get max contribution for each account
    account_type_contributions = {at[0]: 0 for at in constants.ACCOUNT_TYPES}
    if plan.max_employer_match_percent:
        if plan.max_employer_match_percent > 0:
            match = True
        else:
            match = False
    else:
        match = False

    transcript_data = plan.client.regional_data.get('tax_transcript_data')
    if transcript_data:
        if plan.client.regional_data['tax_transcript_data']['sections'][0]['fields']['FILING STATUS'] == 'Married Filing Joint':
            joint = True
        else:
            joint = False
    else:
        joint = False

    if plan.client.employment_status == constants.EMPLOYMENT_STATUS_FULL_TIME or \
       plan.client.employment_status == constants.EMPLOYMENT_STATUS_PART_TIME:
        has_401k = True
    else:
        has_401k = False

    if plan.client.date_of_birth < (datetime.now().date() - relativedelta(years=50)):
        # total including employer is 53k
        max_contributions_pre_tax = 18000
    else:
        # total including employer is 56k
        max_contributions_pre_tax = 24000

    roth_first = False

    if plan.client.employment_status == constants.EMPLOYMENT_STATUS_SELF_EMPLOYED:
        # self employed
        if plan.income >= 27500:
            # sep ira pre tax up to 53000
            account_type_contributions[constants.ACCOUNT_TYPE_IRA] += 53000
        else:
            # roth ira post tax up to 5,500/6,600
            account_type_contributions[constants.ACCOUNT_TYPE_ROTHIRA] += 6600

    elif plan.client.employment_status == constants.EMPLOYMENT_STATUS_UNEMPLOYED:
        # unemployed
        # income or dependent on spouse?
        if plan.income > 0 or joint:
            #  If over 131k single/193k joint
            # pre-tax trad IRA up to 5,500/6,600
            account_type_contributions[constants.ACCOUNT_TYPE_IRA] += 6600
        else:
            # Roth IRA up to 5,500/6,600
            account_type_contributions[constants.ACCOUNT_TYPE_ROTHIRA] += 6600

    else:
        # employed
        if has_401k:
            if match:
                # contribute to 401k up to 18/24k limit
                account_type_contributions[constants.ACCOUNT_TYPE_401K] += 24000

                if (plan.income >= 131000 and not joint) or (plan.income >= 193000 and joint):
                    # over 131k single / 193k joint
                    # contribute remainder to trad IRA up to 5.5/6.5 limit
                    account_type_contributions[constants.ACCOUNT_TYPE_IRA] += 24000
                else:
                    # under 131k single / 193k joint
                    # contribute remainder to roth IRA up to 5.5/6.5 limit
                    account_type_contributions[constants.ACCOUNT_TYPE_ROTHIRA] += 6500
            else:
                if (plan.income >= 131000 and not joint) or (plan.income >= 193000 and joint):
                    # over 131k single / 193k joint
                    # contribute to 401k up to 18/24k limit
                    account_type_contributions[constants.ACCOUNT_TYPE_401K] += 24000
                    # contribute remainder to trad IRA up to 5.5/6.5 limit
                    account_type_contributions[constants.ACCOUNT_TYPE_IRA] += 6500
                else:
                    # under 131k single / 193k joint
                    # contribute to roth IRA up to 5.5/6.5 limit
                    roth_first = True
                    account_type_contributions[constants.ACCOUNT_TYPE_ROTHIRA] += 6500
                    # contribute remainder to 401k up to 18/24k limit
                    account_type_contributions[constants.ACCOUNT_TYPE_ROTH401K] += 24000
        else:
            if (plan.income >= 131000 and not joint) or (plan.income >= 193000 and joint):
                # over 131k single / 193k joint
                # contribute to trad IRA up to 5.5/6.5 limit
                account_type_contributions[constants.ACCOUNT_TYPE_IRA] += 6500
            else:
                # under 131k single / 193k joint
                # contribute to roth IRA up to 5.5/6.5 limit
                account_type_contributions[constants.ACCOUNT_TYPE_ROTHIRA] += 6500
                    
    sorted_contribs = sorted(account_type_contributions, key=account_type_contributions.get, reverse=True)
    rv = [(ac, min(account_type_contributions[ac], max_contributions_pre_tax)) for ac in sorted_contribs]
    if roth_first:
        tmp = rv[1]
        tmp2 = rv[0]
        rv[0] = tmp
        rv[1] = tmp2
    return rv
