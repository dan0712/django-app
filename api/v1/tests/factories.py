# -*- coding: utf-8 -*-
import factory
import decimal
import random
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from django.contrib.auth.models import Group
from django.utils import timezone
from main.models import User, ExternalAsset, PortfolioSet, Firm, Advisor, \
                        Goal, GoalType, InvestmentType, AssetClass, Ticker, \
                        Transaction, GoalSetting, GoalMetricGroup, \
                        FiscalYear, DailyPrice, MarketCap, MarketIndex, \
                        GoalMetric, AssetFeatureValue, AssetFeature, \
                        MarkowitzScale, Supervisor, AuthorisedRepresentative, PositionLot, ExecutionDistribution,\
                        InvestmentCycleObservation, InvestmentCyclePrediction, \
                        RecurringTransaction, AccountGroup, Platform

from retiresmartz.models import RetirementPlan, RetirementAdvice
from main.models import Region as MainRegion
from client.models import Client, ClientAccount, RiskProfileGroup, \
    RiskProfileQuestion, RiskProfileAnswer, \
    AccountTypeRiskProfileGroup, EmailInvite
from statements.models import StatementOfAdvice, RecordOfAdvice
from user.models import SecurityQuestion, SecurityAnswer
from address.models import Address, Region
from django.contrib.contenttypes.models import ContentType
from random import randrange


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


class InvestmentCycleObservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvestmentCycleObservation

    recorded = factory.Sequence(lambda n: date(year=int(1990 + n), month=1, day=1))
    source = ''


class InvestmentCyclePredictionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvestmentCyclePrediction

    pred_dt = factory.Sequence(lambda n: date(year=int(1990 + n), month=1, day=1))
    source = ''


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: 'Group %d' % n)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: 'Bruce%d' % n)
    last_name = factory.Sequence(lambda n: 'Wayne%d' % n)
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', 'test')

    is_active = True


class PortfolioSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioSet

    name = factory.Sequence(lambda n: 'PortfolioSet %d' % n)
    risk_free_rate = factory.Sequence(lambda n: n * .01)

    @factory.post_generation
    def asset_classes(self, create, items, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if items:
            # A list of groups were passed in, use them
            for item in items:
                self.asset_classes.add(item)


class FiscalYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FiscalYear

    name = factory.Sequence(lambda n: 'FiscalYear %d' % n)
    year = factory.Sequence(lambda n: int(1990 + n))
    begin_date = factory.Sequence(lambda n: datetime(year=int(1990 + n), month=1, day=1))
    end_date = factory.Sequence(lambda n: datetime(year=int(1990 + n), month=12, day=20))
    month_ends = '31,29,31,30,31,30,31,31,30,31,30,31'


class FirmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Firm

    name = factory.Sequence(lambda n: 'Firm %d' % n)
    token = factory.Sequence(lambda n: 'Token %d' % n)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)
    slug = factory.Sequence(lambda n: 'Slug %d' % n)
    logo = factory.django.ImageField(filename='some_firm_logo.jpg')
    knocked_out_logo = factory.django.ImageField(filename='some_colored_logo.jpg')


class RiskProfileGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskProfileGroup

    name = factory.Sequence(lambda n: 'RiskProfileGroup %d' % n)


class StaffUserFactory(UserFactory):
    is_staff = True


class SuperUserFactory(UserFactory):
    is_superuser = True


class SecurityQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SecurityQuestion

    question = factory.Sequence(lambda n: 'Question %d' % n)


class SecurityAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SecurityAnswer

    user = factory.SubFactory(UserFactory)
    question = factory.Sequence(lambda n: "Question %d" % n)
    answer = factory.PostGenerationMethodCall('set_answer', 'test')


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    name = factory.Sequence(lambda n: "Region %d" % n)
    # not real postal codes but should work for testing purposes
    code = factory.Sequence(lambda n: '%d' % n)
    country = 'US'


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    address = factory.Sequence(lambda n: "Address %d" % n)
    # not real postal codes but should work for testing purposes
    post_code = factory.Sequence(lambda n: '%d' % n)
    region = factory.SubFactory(RegionFactory)


class AdvisorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advisor

    user = factory.SubFactory(UserFactory)
    firm = factory.SubFactory(FirmFactory)
    betasmartz_agreement = True
    residential_address = factory.SubFactory(AddressFactory)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)


class AuthorisedRepresentativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuthorisedRepresentative

    user = factory.SubFactory(UserFactory)
    firm = factory.SubFactory(FirmFactory)
    letter_of_authority = factory.django.FileField(filename='tests/test_letter_of_authority.txt')
    betasmartz_agreement = True
    is_accepted = True
    is_confirmed = True

    residential_address = factory.SubFactory(AddressFactory)


class AccountTypeRiskProfileGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountTypeRiskProfileGroup

    account_type = factory.Sequence(lambda n: int(n))
    risk_profile_group = factory.SubFactory(RiskProfileGroupFactory)


class RiskProfileQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskProfileQuestion

    group = factory.SubFactory(RiskProfileGroupFactory)
    order = factory.Sequence(lambda n: int(n))
    text = factory.Sequence(lambda n: 'RiskProfileQuestion %d' % n)


class RiskProfileAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskProfileAnswer

    question = factory.SubFactory(RiskProfileQuestionFactory)
    order = factory.Sequence(lambda n: int(n))
    text = factory.Sequence(lambda n: 'RiskProfileAnswer %d' % n)
    b_score = factory.Sequence(lambda n: float(n))
    a_score = factory.Sequence(lambda n: float(n))
    s_score = factory.Sequence(lambda n: float(n))


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    advisor = factory.SubFactory(AdvisorFactory)
    user = factory.SubFactory(UserFactory)
    residential_address = factory.SubFactory(AddressFactory)
    occupation = factory.Sequence(lambda n: 'Occupation %d' % n)
    employer = factory.Sequence(lambda n: 'Employer %d' % n)
    income = factory.LazyAttribute(lambda n: float(random.randrange(1000000)))
    risk_profile_group = factory.SubFactory(RiskProfileGroupFactory)
    # risk_profile_responses = factory.SubFactory(RiskProfileAnswerFactory)
    # lets use a random date from last 18-70 years for dob
    date_of_birth = factory.LazyAttribute(lambda n: random_date(datetime.now().date() - relativedelta(years=70),
                                                                datetime.now().date() - relativedelta(years=18)))
    is_confirmed = True
    is_accepted = True


class EmailInviteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailInvite
    advisor = factory.SubFactory(AdvisorFactory)
    first_name = factory.Sequence(lambda n: 'Invite%d' % n)
    last_name = factory.Sequence(lambda n: 'Friendly%d' % n)
    email = factory.Sequence(lambda n: 'invite%s@example.com' % n)


class ClientAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientAccount

    primary_owner = factory.SubFactory(ClientFactory)
    account_type = 0  # 0 for personal account type
    account_name = factory.Sequence(lambda n: 'ClientAccount %d' % n)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)
    confirmed = True
    cash_balance = factory.LazyAttribute(lambda n: float(random.randrange(10000000)) / 100)


class StatementOfAdviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StatementOfAdvice

    account = factory.SubFactory(ClientAccountFactory)


class RecordOfAdviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecordOfAdvice

    account = factory.SubFactory(ClientAccountFactory)


class AssetFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssetFeature

    name = factory.Sequence(lambda n: 'AssetFeature %d' % n)


class AssetFeatureValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssetFeatureValue

    name = factory.Sequence(lambda n: 'AssetFeatureValue %d' % n)
    feature = factory.SubFactory(AssetFeatureFactory)

    @factory.post_generation
    def assets(self, create, items, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if items:
            # A list of groups were passed in, use them
            for item in items:
                self.assets.add(item)


class GoalMetricFactory(factory.django.DjangoModelFactory):
    """
    By default create a random risk score metric.
    """
    class Meta:
        model = GoalMetric

    type = factory.Sequence(lambda n: random.randint(0, 1))
    comparison = factory.Sequence(lambda n: random.randint(0, 2))
    rebalance_type = factory.Sequence(lambda n: random.randint(0, 1))
    rebalance_thr = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    configured_val = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))


class GoalMetricGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalMetricGroup


class GoalSettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalSetting

    target = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    completion = factory.LazyAttribute(lambda n: random_date(datetime.today().date(), (datetime.today() + relativedelta(years=30)).date()))
    hedge_fx = False
    metric_group = factory.SubFactory(GoalMetricGroupFactory)


class GoalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalType

    name = factory.Sequence(lambda n: "GoalType %d" % n)
    default_term = factory.LazyAttribute(lambda n: int(random.randrange(100)))
    risk_sensitivity = factory.LazyAttribute(lambda n: float(random.randrange(1000) / 100))


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    account = factory.SubFactory(ClientAccountFactory)
    name = factory.Sequence(lambda n: "Goal %d" % n)
    cash_balance = factory.LazyAttribute(lambda n: float(random.randrange(1000000)) / 100)
    type = factory.SubFactory(GoalTypeFactory)
    portfolio_set = factory.SubFactory(PortfolioSetFactory)

    selected_settings = factory.SubFactory(GoalSettingFactory)


class ExternalAssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExternalAsset

    name = factory.Sequence(lambda n: "ExternalAsset %d" % n)
    owner = factory.SubFactory(ClientFactory)
    valuation = factory.LazyAttribute(lambda n: decimal.Decimal(random.randrange(1000000)) / 100)
    valuation_date = factory.LazyAttribute(lambda n: random_date(datetime.today() - relativedelta(days=30), datetime.today()).date())
    growth = decimal.Decimal('0.01')
    acquisition_date = factory.LazyFunction(datetime.now().date)

    type = factory.LazyAttribute(lambda n: random.randrange(7))
    # class Type(ChoiceEnum):
    #     FAMILY_HOME = (0, 'Family Home')
    #     INVESTMENT_PROPERTY = (1, 'Investment Property')
    #     INVESTMENT_PORTFOLIO = (2, 'Investment Portfolio')
    #     SAVINGS_ACCOUNT = (3, 'Savings Account')
    #     PROPERTY_LOAN = (4, 'Property Loan')
    #     TRANSACTION_ACCOUNT = (5, 'Transaction Account')
    #     RETIREMENT_ACCOUNT = (6, 'Retirement Account')
    #     OTHER = (7, 'Other')


class InvestmentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InvestmentType

    name = factory.Sequence(lambda n: 'InvestmentType %d' % n)


class AssetClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssetClass

    name = factory.Sequence(lambda n: 'AssetClass %d' % n)
    display_order = factory.Sequence(lambda n: int(n))
    investment_type = factory.SubFactory(InvestmentTypeFactory)


class ContentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentType


class MainRegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MainRegion

    name = factory.Sequence(lambda n: 'Region %d' % n)


class MarketIndexFactory(factory.django.DjangoModelFactory):
    """
    Generic relation with MarketCap
    Generic relation with DailyPrice
    Generic relation with Ticker
    """
    class Meta:
        model = MarketIndex

    region = factory.SubFactory(MainRegionFactory)
    data_api_param = factory.Sequence(lambda n: str(n))


class MarkowitzScaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MarkowitzScale

    date = datetime.today()
    min = 0.002
    max = 10.269
    a = 1.38034074450515
    b = 1.04131482565774
    c = -0.180340744505146


class MarketCapFactory(factory.django.DjangoModelFactory):
    """
    unique_together = ("instrument_content_type", "instrument_object_id", "date")

    instrument_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    instrument_object_id = models.PositiveIntegerField()
    instrument = GenericForeignKey('instrument_content_type', 'instrument_object_id')
    date = models.DateField()
    value = models.FloatField()
    """
    class Meta:
        model = MarketCap

    # instrument_content_type = factory.SubFactory(ContentTypeFactory)
    instrument = factory.SubFactory(MarketIndexFactory)
    date = factory.Sequence(lambda n: (datetime.today() - relativedelta(days=n+5)).date())
    value = factory.LazyAttribute(lambda n: float(random.randrange(1000) / 100))


class TickerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticker

    symbol = factory.Sequence(lambda n: str(n))
    ordering = factory.Sequence(lambda n: int(n))
    asset_class = factory.SubFactory(AssetClassFactory)
    benchmark = factory.SubFactory(MarketIndexFactory)
    region = factory.SubFactory(MainRegionFactory)
    data_api_param = factory.Sequence(lambda n: str(n))


class TransactionFactory(factory.django.DjangoModelFactory):
    """
    Create an example deposit transaction for a new goal.
    """
    class Meta:
        model = Transaction

    reason = Transaction.REASON_DEPOSIT
    amount = factory.LazyAttribute(lambda n: float(random.randrange(1000000)) / 100)
    to_goal = factory.SubFactory(GoalFactory)


class PositionLotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PositionLot


class ExecutionDistributionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExecutionDistribution


class DailyPriceFactory(factory.django.DjangoModelFactory):
    """
    DailyPriceFactory uses TickerFacory for the instrument by default.
    """
    class Meta:
        model = DailyPrice

    #instrument_object_id = factory.LazyAttribute(lambda obj: obj.instrument.id)
    instrument = factory.SubFactory(TickerFactory)
    date = factory.Sequence(lambda n: (datetime.today() - relativedelta(days=n + 5)).date())
    price = factory.LazyAttribute(lambda n: float(random.randrange(100) / 10))


class GoalMetricFactory(factory.django.DjangoModelFactory):
    """
    By default create a random risk score metric.
    """
    class Meta:
        model = GoalMetric
    group = factory.SubFactory(GoalMetricGroupFactory)
    type = GoalMetric.METRIC_TYPE_RISK_SCORE
    comparison = GoalMetric.METRIC_COMPARISON_EXACTLY
    rebalance_type = factory.sequence(lambda n: random.randint(0, 1))
    rebalance_thr = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    configured_val = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))


class SupervisorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supervisor

    user = factory.SubFactory(UserFactory)
    firm = factory.SubFactory(FirmFactory)


class AuthorisedRepresentativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuthorisedRepresentative

    user = factory.SubFactory(UserFactory)
    firm = factory.SubFactory(FirmFactory)
    letter_of_authority = factory.django.FileField(filename='tests/test_letter_of_authority.txt')
    betasmartz_agreement = True
    is_accepted = True
    is_confirmed = True

    residential_address = factory.SubFactory(AddressFactory)


class RetirementPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RetirementPlan
    name = factory.Sequence(lambda n: 'RetirementPlan %d' % n)
    client = factory.SubFactory(ClientFactory)
    retirement_age = 55
    calculated_life_expectancy = 80
    selected_life_expectancy = 80
    desired_income = 250000
    income = 100000
    btc = 0
    atc = 0
    volunteer_days = factory.LazyAttribute(lambda n: random.randrange(7))
    paid_days = factory.LazyAttribute(lambda n: random.randrange(7))
    same_home = False
    same_location = False
    retirement_postal_code = 11901
    reverse_mortgage = True
    expected_return_confidence = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    desired_risk = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    recommended_risk = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    max_risk = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))


class RecurringTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecurringTransaction
    setting = factory.SubFactory(GoalSettingFactory)
    begin_date = timezone.now().date()
    amount = factory.LazyAttribute(lambda n: int(random.randrange(10000)))
    growth = factory.LazyAttribute(lambda n: float(random.randrange(100) / 100))
    schedule = factory.Sequence(lambda n: 'RRULE %s' % n)


class RetirementAdviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RetirementAdvice

    plan = factory.SubFactory(RetirementPlanFactory)
    # trigger = factory.SubFactory(EventLogFactory)
    text = factory.Sequence(lambda n: 'Retirement Advice %s' % n)


class AccountGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountGroup

    name = factory.Sequence(lambda n: 'Account Group %s' % n)
    advisor = factory.SubFactory(AdvisorFactory)

    # @factory.post_generation
    # def secondary_advisors(self, create, extracted, **kwargs):
    #     if not create:
    #         return
    #     if extracted:
    #         for advisor in extracted:
    #             self.secondary_advisors.add(advisor)


class PlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Platform

    portfolio_set = factory.SubFactory(PortfolioSetFactory)
