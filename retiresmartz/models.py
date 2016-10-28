from __future__ import unicode_literals

import logging

from django.core.validators import MaxLengthValidator, MaxValueValidator, \
    MinLengthValidator, MinValueValidator, ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from jsonfield.fields import JSONField
from pinax.eventlog.models import Log

from common.structures import ChoiceEnum
from main.models import TransferPlan
from retiresmartz.managers import RetirementAdviceQueryset
from .managers import RetirementPlanQuerySet

logger = logging.getLogger(__name__)


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
        help_text="The desired annual household pre-tax retirement "
                  "income in system currency")
    income = models.PositiveIntegerField(
        help_text="The current annual personal pre-tax income at "
                  "the start of your plan")

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
        help_text="The price of your future retirement home "
                  "(in today's dollars)")

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
                                 help_text="List of deposits [{id, desc, cat, who, amt},...]")

    income_growth = models.FloatField(default=0,
                                      help_text="Above consumer price index "
                                                "(inflation)")
    expected_return_confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)],
                                                   help_text="Planned confidence of the portfolio returns given the "
                                                             "volatility and risk predictions.")

    retirement_age = models.PositiveIntegerField()

    btc = models.PositiveIntegerField(help_text="Annual personal before-tax "
                                                "contributions")
    atc = models.PositiveIntegerField(help_text="Annual personal after-tax "
                                                "contributions")

    max_employer_match_percent = models.FloatField(
        null=True, blank=True,
        help_text="The percent the employer matches of before-tax contributions"
    )

    desired_risk = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The selected risk appetite for this retirement plan")

    recommended_risk = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The calculated recommended risk for this retirement plan")

    max_risk = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The maximum allowable risk appetite for this retirement "
                  "plan, based on our risk model")

    # calculated_life_expectancy should be calculated,
    # read-only don't let client create/update
    # TODO: Always Calculate the below value in the save(). Make it editable=False, null=False, blank=True
    calculated_life_expectancy = models.PositiveIntegerField(blank=True, null=True)
    # TODO: This field should be blank=True and also calculated if not set on save().
    selected_life_expectancy = models.PositiveIntegerField()

    agreed_on = models.DateTimeField(null=True, blank=True)

    portfolio = JSONField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        """
        Override save() so we can do some custom validation of partner plans.
        """
        if self.was_agreed:
            raise ValidationError("Cannot save a RetirementPlan that has "
                                  "been agreed upon")

        reverse_plan = getattr(self, 'partner_plan_reverse', None)
        if self.partner_plan is not None and reverse_plan is not None and \
                        self.partner_plan != reverse_plan:
            raise ValidationError(
                "Partner plan relationship must be symmetric."
            )

        super(RetirementPlan, self).save(*args, **kwargs)

        if self.agreed_on and not self.was_agreed and not self.get_soa():
            self.generate_soa()

    def get_soa(self):
        from statements.models import RetirementStatementOfAdvice
        qs = RetirementStatementOfAdvice.objects.filter(
            retirement_plan_id=self.pk
        )
        if qs.count():
            self.statement_of_advice = qs[0]
            return qs[0]
        elif self.agreed_on:
            return self.generate_soa()
        return None

    def generate_soa(self):
        from statements.models import RetirementStatementOfAdvice
        if not self.agreed_on:
            raise Exception('Can only generate SOA on an agreed plan')
        soa = RetirementStatementOfAdvice(retirement_plan_id=self.id)
        soa.save()
        return soa


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
    plan = models.ForeignKey(RetirementPlan, related_name='retiree')
    account = models.OneToOneField('client.ClientAccount',
                                   related_name='retirement')


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
    plan = models.ForeignKey(RetirementPlan, related_name='advice')
    trigger = models.ForeignKey(Log, related_name='advice')
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
