import datetime

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from pinax.eventlog.models import Log

import address.models as ad
from api.v1.tests.factories import GoalMetricFactory, TransactionFactory, PositionLotFactory, \
    ExecutionDistributionFactory, ExecutionFactory
from client.models import Client, ClientAccount, RiskProfileAnswer,\
    RiskProfileGroup, RiskProfileQuestion, IBAccount
from main.constants import ACCOUNT_TYPE_PERSONAL
from main.event import Event
from main.models import Advisor, AssetClass, DailyPrice, Execution, \
    ExecutionDistribution, ExternalAsset, Firm, Goal, GoalMetricGroup, \
    GoalSetting, GoalType, HistoricalBalance, MarketIndex, MarketOrderRequest,\
    PortfolioSet, Region, Ticker, Transaction, User, ExternalInstrument, ExecutionRequest
from main.risk_profiler import MINIMUM_RISK

from retiresmartz.models import RetirementPlan


class Fixture1:
    @classmethod
    def portfolioset1(cls):
        params = {
            'name': 'portfolioset1',
            'risk_free_rate': 0.02,
        }
        return PortfolioSet.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def portfolioset2(cls):
        params = {
            'name': 'portfolioset2',
            'risk_free_rate': 0.02,
        }
        return PortfolioSet.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def firm1(cls):
        params = {
            'name': 'example_inc',
            'token': 'example_inc',
            'default_portfolio_set': Fixture1.portfolioset1(),
        }
        return Firm.objects.get_or_create(slug='example_inc', defaults=params)[0]


    @classmethod
    def user_group_advisors(cls):
        return Group.objects.get_or_create(name=User.GROUP_ADVISOR)[0]

    @classmethod
    def user_group_clients(cls):
        return Group.objects.get_or_create(name=User.GROUP_CLIENT)[0]

    @classmethod
    def advisor1_user(cls):
        params = {
            'first_name': "test",
            'last_name': "advisor",
        }
        i, c = User.objects.get_or_create(email="advisor@example.com", defaults=params)
        if c:
            i.groups.add(Fixture1.user_group_advisors())
        return i

    @classmethod
    def address1(cls):
        region = ad.Region.objects.get_or_create(name='Here', country='AU')[0]
        return ad.Address.objects.get_or_create(address='My House', post_code='1000', region=region)[0]

    @classmethod
    def address2(cls):
        region = ad.Region.objects.get_or_create(name='Here', country='AU')[0]
        return ad.Address.objects.get_or_create(address='My House 2', post_code='1000', region=region)[0]

    @classmethod
    def advisor1(cls):
        params = {
            'firm': Fixture1.firm1(),
            'betasmartz_agreement': True,
            'default_portfolio_set': Fixture1.portfolioset1(),
            'residential_address': Fixture1.address1(),
        }
        return Advisor.objects.get_or_create(user=Fixture1.advisor1_user(), defaults=params)[0]

    @classmethod
    def client1_user(cls):
        params = {
            'first_name': "test",
            'last_name': "client",
        }
        i, c = User.objects.get_or_create(email="client@example.com", defaults=params)
        if c:
            i.groups.add(Fixture1.user_group_clients())
        return i

    @classmethod
    def client2_user(cls):
        params = {
            'first_name': "test",
            'last_name': "client_2",
        }
        return User.objects.get_or_create(email="client2@example.com", defaults=params)[0]

    @classmethod
    def client1(cls):
        params = {
            'advisor': Fixture1.advisor1(),
            'user': Fixture1.client1_user(),
            'date_of_birth': datetime.date(1970, 1, 1),
            'residential_address': Fixture1.address2(),
            'risk_profile_group': Fixture1.risk_profile_group1(),
        }
        return Client.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def client2(cls):
        params = {
            'advisor': Fixture1.advisor1(),
            'user': Fixture1.client2_user(),
            'date_of_birth': datetime.date(1980, 1, 1),
            'residential_address': Fixture1.address2(),
            'risk_profile_group': Fixture1.risk_profile_group2(),
        }
        return Client.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def client1_retirementplan1(cls):
        return RetirementPlan.objects.get_or_create(id=1, defaults={
            'name': 'Plan1',
            'client': Fixture1.client1(),
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'same_home': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
            'retirement_age': 65,
            'btc': 50000,
            'atc': 30000,
            'desired_risk': 0.6,
            'recommended_risk': 0.5,
            'max_risk': 1.0,
            'calculated_life_expectancy': 73,
            'selected_life_expectancy': 80,
        })[0]

    @classmethod
    def client2_retirementplan1(cls):
        return RetirementPlan.objects.get_or_create(id=2, defaults={
            'name': 'Plan1',
            'client': Fixture1.client2(),
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'same_home': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
            'retirement_age': 65,
            'btc': 50000,
            'atc': 30000,
            'desired_risk': 0.6,
            'recommended_risk': 0.5,
            'max_risk': 1.0,
            'calculated_life_expectancy': 73,
            'selected_life_expectancy': 80,
                                                    })[0]

    @classmethod
    def client2_retirementplan2(cls):
        return RetirementPlan.objects.get_or_create(id=4, defaults={
            'name': 'Plan2',
            'client': Fixture1.client2(),
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'same_home': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
            'retirement_age': 65,
            'btc': 50000,
            'atc': 30000,
            'desired_risk': 0.6,
            'recommended_risk': 0.5,
            'max_risk': 1.0,
            'calculated_life_expectancy': 73,
            'selected_life_expectancy': 80,
                                                    })[0]

    @classmethod
    def client1_partneredplan(cls):
        plan1 = Fixture1.client1_retirementplan1()
        plan2 = Fixture1.client2_retirementplan1()
        plan1.partner_plan = plan2
        plan2.partner_plan = plan1
        plan1.save()
        plan2.save()
        return plan1

    @classmethod
    def risk_profile_group1(cls):
        return RiskProfileGroup.objects.get_or_create(name='risk_profile_group1')[0]

    @classmethod
    def risk_profile_group2(cls):
        return RiskProfileGroup.objects.get_or_create(name='risk_profile_group2')[0]

    @classmethod
    def risk_profile_question1(cls):
        return RiskProfileQuestion.objects.get_or_create(group=Fixture1.risk_profile_group1(),
                                                         order=0,
                                                         text='How much do you like risk?')[0]

    @classmethod
    def risk_profile_question2(cls):
        return RiskProfileQuestion.objects.get_or_create(group=Fixture1.risk_profile_group1(),
                                                         order=1,
                                                         text='How sophisticated are you?')[0]

    @classmethod
    def risk_profile_question3(cls):
        return RiskProfileQuestion.objects.get_or_create(group=Fixture1.risk_profile_group1(),
                                                         order=2,
                                                         text='Have you used other wealth management software?')[0]

    @classmethod
    def risk_profile_answer1a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=0,
                                                       text='A lot',
                                                       b_score=9,
                                                       a_score=9,
                                                       s_score=9)[0]

    @classmethod
    def risk_profile_answer1b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=1,
                                                       text='A little',
                                                       b_score=2,
                                                       a_score=2,
                                                       s_score=2)[0]

    @classmethod
    def risk_profile_answer1c(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=2,
                                                       text="I'm smart but scared",
                                                       b_score=1,
                                                       a_score=9,
                                                       s_score=9)[0]

    @classmethod
    def risk_profile_answer1d(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=3,
                                                       text="I'm clueless and wild",
                                                       b_score=9,
                                                       a_score=1,
                                                       s_score=1)[0]

    @classmethod
    def risk_profile_answer2a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=0,
                                                       text='Very',
                                                       b_score=9,
                                                       a_score=9,
                                                       s_score=9)[0]

    @classmethod
    def risk_profile_answer2b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=1,
                                                       text="I'm basically a peanut",
                                                       b_score=1,
                                                       a_score=1,
                                                       s_score=1)[0]

    @classmethod
    def risk_profile_answer2c(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=2,
                                                       text="I'm smart but scared",
                                                       b_score=1,
                                                       a_score=9,
                                                       s_score=9)[0]

    @classmethod
    def risk_profile_answer2d(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=3,
                                                       text="I'm clueless and wild",
                                                       b_score=9,
                                                       a_score=1,
                                                       s_score=1)[0]

    @classmethod
    def risk_profile_answer3a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question3(),
                                                       order=0,
                                                       text='Yes',
                                                       b_score=9,
                                                       a_score=9,
                                                       s_score=9)[0]
    @classmethod
    def risk_profile_answer3b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question3(),
                                                       order=1,
                                                       text='No',
                                                       b_score=1,
                                                       a_score=1,
                                                       s_score=1)[0]

    @classmethod
    def populate_risk_profile_questions(cls):
        Fixture1.risk_profile_question1()
        Fixture1.risk_profile_answer1a()
        Fixture1.risk_profile_answer1b()
        Fixture1.risk_profile_question2()
        Fixture1.risk_profile_answer2a()
        Fixture1.risk_profile_answer2b()
        # Don't create question3 here, we use that to test validation
        # that risk is NEUTRAL when the questions have changed

    @classmethod
    def populate_risk_profile_responses(cls):
        Fixture1.personal_account1().primary_owner.risk_profile_responses.add(Fixture1.risk_profile_answer1a())
        Fixture1.personal_account1().primary_owner.risk_profile_responses.add(Fixture1.risk_profile_answer2a())

    @classmethod
    def ib_account1(cls) -> IBAccount:
        params = {
            'ib_account': 'DU299694',
            'bs_account': Fixture1.personal_account1()
        }
        return IBAccount.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def ib_account2(cls) -> IBAccount:
        params = {
            'ib_account': 'DU299695',
            'bs_account': Fixture1.personal_account2()
        }
        return IBAccount.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def personal_account1(cls) -> ClientAccount:
        params = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'primary_owner': Fixture1.client1(),
            'default_portfolio_set': Fixture1.portfolioset1(),
            'confirmed': True,
        }
        return ClientAccount.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def personal_account2(cls) -> ClientAccount:
        params = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'primary_owner': Fixture1.client2(),
            'default_portfolio_set': Fixture1.portfolioset2(),
            'confirmed': True,
        }
        return ClientAccount.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def metric_group1(cls):
        g, c = GoalMetricGroup.objects.get_or_create(type=GoalMetricGroup.TYPE_PRESET,
                                                     name='metricgroup1')
        # A metric group isn't valid without a risk score, and we only want to create the metric if the group was
        # newly created.
        if c:
            GoalMetricFactory.create(group=g, configured_val=MINIMUM_RISK)
        return g

    @classmethod
    def metric_group2(cls):
        g, c = GoalMetricGroup.objects.get_or_create(type=GoalMetricGroup.TYPE_PRESET,
                                                     name='metricgroup2')
        # A metric group isn't valid without a risk score, and we only want to create the metric if the group was
        # newly created.
        if c:
            GoalMetricFactory.create(group=g, configured_val=MINIMUM_RISK)
        return g

    @classmethod
    def settings1(cls):
        return GoalSetting.objects.get_or_create(target=100000,
                                                 completion=datetime.date(2000, 1, 1),
                                                 hedge_fx=False,
                                                 metric_group=Fixture1.metric_group1(),
                                                 rebalance=False)[0]

    @classmethod
    def settings2(cls):
        return GoalSetting.objects.get_or_create(target=100000,
                                                 completion=datetime.date(2000, 1, 1),
                                                 hedge_fx=False,
                                                 metric_group=Fixture1.metric_group2(),
                                                 rebalance=False)[0]

    @classmethod
    def goal_type1(cls):
        return GoalType.objects.get_or_create(name='goaltype1',
                                              default_term=5,
                                              risk_sensitivity=7.0)[0]

    @classmethod
    def goal_type2(cls):
        return GoalType.objects.get_or_create(name='goaltype2',
                                              default_term=5,
                                              risk_sensitivity=7.0)[0]

    @classmethod
    def goal1(cls):
        return Goal.objects.get_or_create(account=Fixture1.personal_account1(),
                                          name='goal1',
                                          type=Fixture1.goal_type1(),
                                          portfolio_set=Fixture1.portfolioset1(),
                                          selected_settings=Fixture1.settings1())[0]

    @classmethod
    def goal2(cls):
        return Goal.objects.get_or_create(account=Fixture1.personal_account2(),
                                          name='goal2',
                                          type=Fixture1.goal_type2(),
                                          portfolio_set=Fixture1.portfolioset2(),
                                          selected_settings=Fixture1.settings2())[0]

    @classmethod
    def settings_event1(cls):
        return Log.objects.get_or_create(user=Fixture1.client1_user(),
                                         timestamp=timezone.make_aware(datetime.datetime(2000, 1, 1)),
                                         action=Event.APPROVE_SELECTED_SETTINGS.name,
                                         extra={'reason': 'Just because'},
                                         defaults={'obj': Fixture1.goal1()})[0]

    @classmethod
    def settings_event2(cls):
        return Log.objects.get_or_create(user=Fixture1.client1_user(),
                                         timestamp=timezone.make_aware(datetime.datetime(2000, 1, 1, 1)),
                                         action=Event.UPDATE_SELECTED_SETTINGS.name,
                                         extra={'reason': 'Just because 2'},
                                         defaults={'obj': Fixture1.goal1()})[0]

    @classmethod
    def transaction_event1(cls):
        # This will populate the associated Transaction as well.
        return Log.objects.get_or_create(user=Fixture1.client1_user(),
                                         timestamp=timezone.make_aware(datetime.datetime(2001, 1, 1)),
                                         action=Event.GOAL_DEPOSIT_EXECUTED.name,
                                         extra={'reason': 'Goal Deposit',
                                                'txid': Fixture1.transaction1().id},
                                         defaults={'obj': Fixture1.goal1()})[0]

    @classmethod
    def transaction1(cls):
        i, c = Transaction.objects.get_or_create(reason=Transaction.REASON_DEPOSIT,
                                                 to_goal=Fixture1.goal1(),
                                                 amount=3000,
                                                 status=Transaction.STATUS_EXECUTED,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1)),
                                                 executed=timezone.make_aware(datetime.datetime(2001, 1, 1)))

        if c:
            i.created = timezone.make_aware(datetime.datetime(2000, 1, 1))
            i.save()

        return i


    @classmethod
    def transaction2(cls):
        i, c = Transaction.objects.get_or_create(reason=Transaction.REASON_ORDER,
                                                 to_goal=Fixture1.goal1(),
                                                 amount=3000,
                                                 status=Transaction.STATUS_PENDING,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1))
                                                 )

        if c:
            i.created = timezone.make_aware(datetime.datetime(2000, 1, 1))
            i.save()
        return i

    @classmethod
    def pending_deposit1(cls):
        i, c = Transaction.objects.get_or_create(reason=Transaction.REASON_DEPOSIT,
                                                 to_goal=Fixture1.goal1(),
                                                 amount=4000,
                                                 status=Transaction.STATUS_PENDING,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1, 1)))
        if c:
            i.created = timezone.make_aware(datetime.datetime(2000, 1, 1, 1))
            i.save()

        return i

    @classmethod
    def pending_withdrawal1(cls):
        i, c = Transaction.objects.get_or_create(reason=Transaction.REASON_DEPOSIT,
                                                 from_goal=Fixture1.goal1(),
                                                 amount=3500,
                                                 status=Transaction.STATUS_PENDING,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1, 2)))
        if c:
            i.created = timezone.make_aware(datetime.datetime(2000, 1, 1, 2))
            i.save()

        return i

    @classmethod
    def populate_balance1(cls):
        HistoricalBalance.objects.get_or_create(goal=Fixture1.goal1(),
                                                date=datetime.date(2000, 12, 31),
                                                balance=0)
        HistoricalBalance.objects.get_or_create(goal=Fixture1.goal1(),
                                                date=datetime.date(2001, 1, 1),
                                                balance=3000)

    @classmethod
    def asset_class1(cls):
        params = {
            'display_order': 0,
            'display_name': 'Test Asset Class 1',
            'investment_type_id': 2,  # STOCKS pk 2, BONDS pk 1, MIXED pk 3
        }
        # Asset class name needs to be upper case.
        return AssetClass.objects.get_or_create(name='ASSETCLASS1', defaults=params)[0]

    @classmethod
    def region1(cls):
        return Region.objects.get_or_create(name='TestRegion1')[0]

    @classmethod
    def market_index1(cls):
        params = {
            'display_name': 'Test Market Index 1',
            'url': 'nowhere.com',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'MI1',
        }
        return MarketIndex.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def market_index1_daily_prices(cls):
        prices = [100, 110, 105, 103, 107]
        start_date = datetime.date(2016, 4, 1)
        d = start_date
        fund = cls.market_index1()
        for p in prices:
            fund.daily_prices.create(date=d, price=p)
            d += datetime.timedelta(1)

    @classmethod
    def market_index2(cls):
        params = {
            'display_name': 'Test Market Index 2',
            'url': 'nowhere.com',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'MI2',
        }
        return MarketIndex.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def fund1(cls):
        params = {
            'display_name': 'Test Fund 1',
            'url': 'nowhere.com/1',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'ordering': 0,
            'asset_class': Fixture1.asset_class1(),
            'benchmark': Fixture1.market_index1(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'FUND1',
        }
        return Ticker.objects.get_or_create(symbol='TSTSYMBOL1', defaults=params)[0]

    @classmethod
    def fund2(cls):
        params = {
            'display_name': 'Test Fund 2',
            'url': 'nowhere.com/2',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'ordering': 1,
            'asset_class': Fixture1.asset_class1(),
            'benchmark': Fixture1.market_index2(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'FUND2',
        }
        return Ticker.objects.get_or_create(symbol='TSTSYMBOL2', defaults=params)[0]

    @classmethod
    def fund3(cls):
        params = {
            'display_name': 'Test Fund 2',
            'url': 'nowhere.com/2',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'ordering': 1,
            'asset_class': Fixture1.asset_class1(),
            'benchmark': Fixture1.market_index2(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'FUND3',
        }
        return Ticker.objects.get_or_create(symbol='SPY', defaults=params)[0]

    @classmethod
    def fund4(cls):
        params = {
            'display_name': 'Test Fund 2',
            'url': 'nowhere.com/2',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'ordering': 1,
            'asset_class': Fixture1.asset_class1(),
            'benchmark': Fixture1.market_index2(),
            'data_api': 'portfolios.api.bloomberg',
            'data_api_param': 'FUND4',
        }
        return Ticker.objects.get_or_create(symbol='TLT', defaults=params)[0]

    @classmethod
    def external_instrument1(cls):
        params = {
            'institution': ExternalInstrument.Institution.APEX.value,
            'instrument_id': 'SPY_APEX',
            'ticker': Fixture1.fund3()
        }
        return ExternalInstrument.objects.get_or_create(id=1,defaults=params)[0]

    @classmethod
    def external_instrument2(cls):
        params = {
            'institution': ExternalInstrument.Institution.INTERACTIVE_BROKERS.value,
            'instrument_id': 'SPY_IB',
            'ticker': Fixture1.fund3()
        }
        return ExternalInstrument.objects.get_or_create(id=2,defaults=params)[0]

    @classmethod
    def external_debt_1(cls):
        params = {
            'type': ExternalAsset.Type.PROPERTY_LOAN.value,
            # description intentionally omitted to test optionality
            'valuation': '-145000',
            'valuation_date': datetime.date(2016, 7, 5),
            'growth': '0.03',
            'acquisition_date': datetime.date(2016, 7, 3),
        }
        return ExternalAsset.objects.get_or_create(name='My Home Loan', owner=Fixture1.client1(), defaults=params)[0]

    @classmethod
    def external_asset_1(cls):
        '''
        Creates and returns an asset with an associated debt.
        :return:
        '''
        params = {
            'type': ExternalAsset.Type.FAMILY_HOME.value,
            'description': 'This is my beautiful home',
            'valuation': '345000.014',
            'valuation_date': datetime.date(2016, 7, 5),
            'growth': '0.01',
            # trasfer_plan intentionally omitted as there isn't one
            'acquisition_date': datetime.date(2016, 7, 3),
            'debt': Fixture1.external_debt_1(),
        }
        return ExternalAsset.objects.get_or_create(name='My Home', owner=Fixture1.client1(), defaults=params)[0]

    @classmethod
    def set_prices(cls, prices):
        """
        Sets the prices for the given instruments and dates.
        :param prices:
        :return:
        """
        for asset, dstr, price in prices:
            DailyPrice.objects.update_or_create(instrument_object_id=asset.id,
                                                instrument_content_type=ContentType.objects.get_for_model(asset),
                                                date=datetime.datetime.strptime(dstr, '%Y%m%d'),
                                                defaults={'price': price})

    @classmethod
    def add_orders(cls, order_details):
        """
        Adds a bunch of orders to the system
        :param order_details: Iterable of (account, order_state) tuples.
        :return: the newly created orders as a list.
        """
        res = []
        for account, state in order_details:
            res.append(MarketOrderRequest.objects.create(state=state.value, account=account))
        return res

    @classmethod
    def add_execution_requests(cls, goal, execution_details, executions):
        execution_requests = []
        for detail, ed in zip(execution_details, executions):
            mor = detail[1]
            execution_requests.append(ExecutionRequest.objects.create(reason=ExecutionRequest.Reason.DRIFT.value,
                                                                      goal=goal,
                                                                      asset=ed.asset,
                                                                      volume=ed.volume,
                                                                      order=mor))
        return execution_requests

    @classmethod
    def add_executions(cls, execution_details):
        """
        Adds a bunch of order executions to the system
        :param execution_details: Iterable of (asset, order, volume, price, amount, time) tuples.
        :return: the newly created executions as a list.
        """
        res = []
        for asset, order, volume, price, amount, time in execution_details:
            res.append(Execution.objects.create(asset=asset,
                                                volume=volume,
                                                order=order,
                                                price=price,
                                                executed=timezone.make_aware(datetime.datetime.strptime(time, '%Y%m%d')),
                                                amount=amount))
        return res

    @classmethod
    def add_execution_distributions(cls, distribution_details, execution_requests):
        """
        Adds a bunch of order execution distributions to the system
        :param distribution_details: Iterable of (execution, volume, goal) tuples.
        :return: the newly created distributions as a list.
        """
        res = []
        for dd, er in zip(distribution_details, execution_requests):
            execution, volume, goal = dd
            amount = abs(execution.amount * volume / execution.volume)
            if volume > 0:
                tx = Transaction.objects.create(reason=Transaction.REASON_EXECUTION,
                                                from_goal=goal,
                                                amount=amount,
                                                status=Transaction.STATUS_EXECUTED,
                                                executed=execution.executed)
            else:
                tx = Transaction.objects.create(reason=Transaction.REASON_EXECUTION,
                                                to_goal=goal,
                                                amount=amount,
                                                status=Transaction.STATUS_EXECUTED,
                                                executed=execution.executed)
            tx.created = execution.executed
            tx.save()

            res.append(ExecutionDistribution.objects.create(execution=execution,
                                                            transaction=tx,
                                                            volume=volume,
                                                            execution_request=er))
        return res

    @classmethod
    def create_execution_details(cls, goal, ticker, quantity, price, executed):
        mor = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        er = ExecutionRequest.objects.create(reason=ExecutionRequest.Reason.DRIFT.value,
                                             goal=goal,
                                             asset=ticker,
                                             volume=quantity,
                                             order=mor)
        execution = ExecutionFactory.create(asset=ticker,
                                            volume=quantity,
                                            order=mor,
                                            price=price,
                                            executed=executed,
                                            amount=quantity*price)
        transaction = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                                to_goal=None,
                                                from_goal=goal,
                                                status=Transaction.STATUS_EXECUTED,
                                                executed=executed,
                                                amount=quantity*price)
        distribution = ExecutionDistributionFactory.create(execution=execution,
                                                           transaction=transaction,
                                                           volume=quantity,
                                                           execution_request=er)
        position_lot = PositionLotFactory.create(quantity=quantity, execution_distribution=distribution)

        return_values = list()
        return_values.extend((mor, execution, transaction, distribution, position_lot))
        return return_values
