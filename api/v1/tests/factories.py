# -*- coding: utf-8 -*-
from main.models import User, ExternalAsset, PortfolioSet, Firm, Advisor, Goal, GoalType
import factory
from user.models import SecurityQuestion, SecurityAnswer
from client.models import Client, ClientAccount, RiskProfileGroup, \
                          RiskProfileQuestion, RiskProfileAnswer, \
                          AccountTypeRiskProfileGroup
import decimal
import random
from datetime import datetime, date
from address.models import Region, Address
from django.contrib.auth.models import Group


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


class PortfolioSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PortfolioSet

    name = factory.Sequence(lambda n: "PortfolioSet %d" % n)
    risk_free_rate = factory.LazyAttribute(lambda n: float(random.randrange(10000)) / 100)


class FirmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Firm

    name = factory.Sequence(lambda n: "Firm %d" % n)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)


class AdvisorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advisor

    user = factory.SubFactory(UserFactory)
    firm = factory.SubFactory(FirmFactory)
    betasmartz_agreement = True
    residential_address = factory.SubFactory(AddressFactory)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)


class RiskProfileGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RiskProfileGroup

    name = factory.Sequence(lambda n: "RiskProfileGroup %d" % n)


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
    score = factory.Sequence(lambda n: float(n))


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    advisor = factory.SubFactory(AdvisorFactory)
    user = factory.SubFactory(UserFactory)
    residential_address = factory.SubFactory(AddressFactory)


class ClientAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientAccount

    primary_owner = factory.SubFactory(ClientFactory)
    account_type = 0  # 0 for personal account type
    account_name = factory.Sequence(lambda n: 'ClientAccount %d' % n)
    default_portfolio_set = factory.SubFactory(PortfolioSetFactory)
    risk_profile_group = factory.SubFactory(RiskProfileGroupFactory)
    # risk_profile_responses = factory.SubFactory(RiskProfileAnswerFactory)
    confirmed = True


class GoalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalType

    name = factory.Sequence(lambda n: "GoalType %d" % n)


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    account = factory.SubFactory(ClientAccountFactory)
    cash_balance = factory.LazyAttribute(lambda n: float(random.randrange(1000000)) / 100)
    type = factory.SubFactory(GoalTypeFactory)


class ExternalAssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExternalAsset

    name = factory.Sequence(lambda n: "ExternalAsset %d" % n)
    owner = factory.SubFactory(ClientFactory)
    valuation = factory.LazyAttribute(lambda n: decimal.Decimal(random.randrange(1000000)) / 100)
    valuation_date = factory.LazyFunction(datetime.now)
    type = factory.LazyAttribute(lambda n: random.randrange(7))
    growth = decimal.Decimal('0.5')
    acquisition_date = factory.LazyFunction(datetime.now)
    # class Type(ChoiceEnum):
    #     FAMILY_HOME = (0, 'Family Home')
    #     INVESTMENT_PROPERTY = (1, 'Investment Property')
    #     INVESTMENT_PORTFOLIO = (2, 'Investment Portfolio')
    #     SAVINGS_ACCOUNT = (3, 'Savings Account')
    #     PROPERTY_LOAN = (4, 'Property Loan')
    #     TRANSACTION_ACCOUNT = (5, 'Transaction Account')
    #     RETIREMENT_ACCOUNT = (6, 'Retirement Account')
    #     OTHER = (7, 'Other')
