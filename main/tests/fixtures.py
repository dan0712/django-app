import datetime

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from pinax.eventlog.models import Log

from main.event import Event
from main.models import ClientAccount, ACCOUNT_TYPE_PERSONAL, Client, Advisor, User, Firm, PortfolioSet, \
    RiskProfileGroup, GoalSetting, GoalMetricGroup, Goal, GoalType, RiskProfileQuestion, RiskProfileAnswer, \
    Transaction, HistoricalBalance, RetirementPlan, TransferPlan, Ticker, AssetClass, STOCKS, SUPER_ASSET_CLASSES, \
    MarketIndex, Region, DailyPrice, MarketOrderRequest, Execution, ExecutionDistribution


class Fixture1:
    @classmethod
    def portfolioset1(cls):
        params = {
            'name': 'portfolioset1',
            'risk_free_rate': 0.02,
        }
        return PortfolioSet.objects.get_or_create(id=1, defaults=params)[0]

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
    def advisor1(cls):
        params = {
            'firm': Fixture1.firm1(),
            'betasmartz_agreement': True,
            'default_portfolio_set': Fixture1.portfolioset1(),
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
            'date_of_birth': datetime.date(1970, 1, 1)
        }
        return Client.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def client2(cls):
        params = {
            'advisor': Fixture1.advisor1(),
            'user': Fixture1.client2_user(),
            'date_of_birth': datetime.date(1980, 1, 1)
        }
        return Client.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def tx1(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 1000,
            'growth': 0,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def tx2(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 0,
            'growth': 0,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=2, defaults=params)[0]

    @classmethod
    def tx3(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 500,
            'growth': 0,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=3, defaults=params)[0]

    @classmethod
    def tx4(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 200,
            'growth': 0.01,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=4, defaults=params)[0]

    @classmethod
    def tx5(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 500,
            'growth': 0,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=5, defaults=params)[0]

    @classmethod
    def tx6(cls):
        params = {
            'begin_date': datetime.date(2016, 1, 1),
            'amount': 200,
            'growth': 0.01,
            'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
        }
        return TransferPlan.objects.get_or_create(id=6, defaults=params)[0]

    @classmethod
    def client1_retirementplan1(cls):
        return RetirementPlan.objects.get_or_create(id=1, defaults={
                                                    'name': 'Plan1',
                                                    'client': Fixture1.client1(),
                                                    'retirement_date': datetime.date(2055, 1, 1),
                                                    'life_expectancy': 80,
                                                    'btc': Fixture1.tx1(),
                                                    'atc': Fixture1.tx2()})[0]

    @classmethod
    def client2_retirementplan1(cls):
        return RetirementPlan.objects.get_or_create(id=2, defaults={
                                                    'name': 'Plan1',
                                                    'client': Fixture1.client2(),
                                                    'retirement_date': datetime.date(2055, 1, 1),
                                                    'life_expectancy': 84,
                                                    'btc': Fixture1.tx3(),
                                                    'atc': Fixture1.tx4()})[0]

    @classmethod
    def client2_retirementplan2(cls):
        return RetirementPlan.objects.get_or_create(id=4, defaults={
                                                    'name': 'Plan2',
                                                    'client': Fixture1.client2(),
                                                    'retirement_date': datetime.date(2055, 1, 1),
                                                    'life_expectancy': 84,
                                                    'btc': Fixture1.tx5(),
                                                    'atc': Fixture1.tx6()})[0]

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
    def risk_profile_answer1a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=0,
                                                       text='A lot',
                                                       score=9)[0]

    @classmethod
    def risk_profile_answer1b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=1,
                                                       text='A little',
                                                       score=2)[0]

    @classmethod
    def risk_profile_answer2a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=0,
                                                       text='Very',
                                                       score=9)[0]

    @classmethod
    def risk_profile_answer2b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=1,
                                                       text="I'm basically a peanut",
                                                       score=1)[0]

    @classmethod
    def populate_risk_profile_questions(cls):
        Fixture1.risk_profile_question1()
        Fixture1.risk_profile_answer1a()
        Fixture1.risk_profile_answer1b()
        Fixture1.risk_profile_question2()
        Fixture1.risk_profile_answer2a()
        Fixture1.risk_profile_answer2b()

    @classmethod
    def populate_risk_profile_responses(cls):
        Fixture1.personal_account1().risk_profile_responses.add(Fixture1.risk_profile_answer1a())
        Fixture1.personal_account1().risk_profile_responses.add(Fixture1.risk_profile_answer2a())

    @classmethod
    def personal_account1(cls):
        params = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'primary_owner': Fixture1.client1(),
            'default_portfolio_set': Fixture1.portfolioset1(),
            'risk_profile_group': Fixture1.risk_profile_group1(),
        }
        return ClientAccount.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def metric_group1(cls):
        return GoalMetricGroup.objects.get_or_create(type=GoalMetricGroup.TYPE_PRESET,
                                                     name='metricgroup1')[0]

    @classmethod
    def settings1(cls):
        return GoalSetting.objects.get_or_create(target=100000,
                                                 completion=datetime.date(2000, 1, 1),
                                                 hedge_fx=False,
                                                 metric_group=Fixture1.metric_group1(),
                                                 rebalance=False)[0]

    @classmethod
    def goal_type1(cls):
        return GoalType.objects.get_or_create(name='goaltype1',
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
        return Transaction.objects.get_or_create(reason=Transaction.REASON_DEPOSIT,
                                                 to_goal=Fixture1.goal1(),
                                                 amount=3000,
                                                 status=Transaction.STATUS_EXECUTED,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1)),
                                                 executed=timezone.make_aware(datetime.datetime(2001, 1, 1)))[0]

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
            'investment_type': STOCKS,
            'super_asset_class': SUPER_ASSET_CLASSES[0][0]
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
            'region': Fixture1.region1()
        }
        return MarketIndex.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def market_index2(cls):
        params = {
            'display_name': 'Test Market Index 2',
            'url': 'nowhere.com',
            'currency': 'AUD',
            'region': Fixture1.region1()
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
            'benchmark': Fixture1.market_index1()
        }
        return Ticker.objects.get_or_create(symbol='TESTSYMBOL1', defaults=params)[0]

    @classmethod
    def fund2(cls):
        params = {
            'display_name': 'Test Fund 2',
            'url': 'nowhere.com/2',
            'currency': 'AUD',
            'region': Fixture1.region1(),
            'ordering': 1,
            'asset_class': Fixture1.asset_class1(),
            'benchmark': Fixture1.market_index2()
        }
        return Ticker.objects.get_or_create(symbol='TESTSYMBOL2', defaults=params)[0]

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
    def add_execution_distributions(cls, distribution_details):
        """
        Adds a bunch of order execution distributions to the system
        :param distribution_details: Iterable of (execution, volume, goal) tuples.
        :return: the newly created distributions as a list.
        """
        res = []
        for execution, volume, goal in distribution_details:
            amount = abs(execution.amount * volume / execution.volume)
            if volume > 0:
                tx = Transaction.objects.create(reason=Transaction.REASON_EXECUTION,
                                                from_goal=goal,
                                                amount=amount,
                                                status=Transaction.STATUS_EXECUTED,
                                                created=execution.executed,
                                                executed=execution.executed)
            else:
                tx = Transaction.objects.create(reason=Transaction.REASON_EXECUTION,
                                                to_goal=goal,
                                                amount=amount,
                                                status=Transaction.STATUS_EXECUTED,
                                                created=execution.executed,
                                                executed=execution.executed)

            res.append(ExecutionDistribution.objects.create(execution=execution,
                                                            transaction=tx,
                                                            volume=volume))
        return res
