import json
from decimal import Decimal
from datetime import date, timedelta

from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

from django.utils import timezone


from pinax.eventlog.models import Log
from rest_framework import status
from rest_framework.test import APITestCase


from api.v1.tests.factories import MarkowitzScaleFactory, GoalTypeFactory
from common.constants import GROUP_SUPPORT_STAFF
from main.event import Event

from main.models import GoalMetric, Execution, Transaction, ExecutionDistribution, Portfolio, Goal
from main.risk_profiler import max_risk
from .factories import ContentTypeFactory, TransactionFactory, PositionLotFactory

from main.management.commands.populate_test_data import populate_prices, populate_cycle_obs, populate_cycle_prediction
from main.models import ActivityLog, ActivityLogEvent, EventMemo, MarketOrderRequest, InvestmentType
from main.tests.fixture import Fixture1
from .factories import GroupFactory, GoalFactory, ClientAccountFactory, GoalSettingFactory, TickerFactory, \
    AssetClassFactory, PortfolioSetFactory, MarketIndexFactory, GoalMetricFactory

from api.v1.goals.serializers import GoalSettingSerializer, GoalCreateSerializer

mocked_now = datetime(2016, 1, 1)


class GoalTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=self.bonds_type)
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.portfolio_set = PortfolioSetFactory.create()
        self.portfolio_set.asset_classes.add(self.bonds_asset_class, self.stocks_asset_class)

        self.risk_score_metric = {
            "type": GoalMetric.METRIC_TYPE_RISK_SCORE,
            "comparison": GoalMetric.METRIC_COMPARISON_EXACTLY,
            "configured_val": 0.4,
            "rebalance_type": GoalMetric.REBALANCE_TYPE_RELATIVE,
            "rebalance_thr": 0.1
        }

    def tearDown(self):
        self.client.logout()

    def test_get_list(self):
        goal = Fixture1.goal1()
        goal.approve_selected()
        url = '/api/v1/goals'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Make sure for the list endpoint, selected settings is an object, but active and approved are null or integer.
        self.assertEqual(response.data[0]['active_settings'], None)
        self.assertEqual(response.data[0]['approved_settings'], response.data[0]['selected_settings']['id'])

    def test_get_detail(self):
        goal = Fixture1.goal1()
        url = '/api/v1/goals/{}'.format(goal.id)
        goal.approve_selected()
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], Fixture1.goal1().id)
        # Make sure for the detail endpoint, selected settings is an object, but active and approved are null or integer.
        self.assertEqual(response.data['active_settings'], None)
        self.assertEqual(response.data['approved_settings'], response.data['selected_settings']['id'])

    def test_get_no_activity(self):
        url = '/api/v1/goals/{}/activity'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_all_activity(self):
        # First add some transactions, balances and eventlogs, and make sure the ActivityLogs are set.
        Fixture1.settings_event1()
        Fixture1.transaction_event1()
        Fixture1.populate_balance1()  # 2 Activity lines
        # We also need to activate the activity logging for the desired event types.
        ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS)
        ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED)
        ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED)

        url = '/api/v1/goals/{}/activity'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # Note the Goal not included in response as it is in request.
        self.assertEqual(response.data[0], {'time': 946684800,
                                            'type': ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS).activity_log.id})  # Setting change approval
        self.assertEqual(response.data[1], {'balance': 0.0,
                                            'time': 978220800,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id})  # Balance
        # Deposit. Note inclusion of amount, as we're looking at it from the goal perspective.
        self.assertEqual(response.data[2], {'amount': 3000.0,
                                            'data': [3000.0],
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED).activity_log.id})
        self.assertEqual(response.data[3], {'balance': 3000.0,
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id})  # Balance

    def test_event_memo(self):
        '''
        Tests event memos and assigning multiple events to one activity log item.
        :return:
        '''
        # Add a public settings event with a memo
        se = Fixture1.settings_event1()
        EventMemo.objects.create(event=se, comment='A memo for e1', staff=False)
        # Add a staff settings event with a memo
        se2 = Fixture1.settings_event2()
        EventMemo.objects.create(event=se2, comment='A memo for e2', staff=True)
        # Add a transaction event without a memo
        Fixture1.transaction_event1()
        # We also need to activate the activity logging for the desired event types.
        # We add selected and update to the same une to test that too
        al = ActivityLog.objects.create(name="Settings Funk", format_str='Settings messed with')
        ActivityLogEvent.objects.create(id=Event.APPROVE_SELECTED_SETTINGS.value, activity_log=al)
        ActivityLogEvent.objects.create(id=Event.UPDATE_SELECTED_SETTINGS.value, activity_log=al)
        ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED)

        url = '/api/v1/goals/{}/activity'.format(Fixture1.goal1().id)
        # Log in as a client and make sure I see the public settings event, and the transaction, not the staff entry.
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['memos'], ['A memo for e1'])
        self.assertFalse('memos' in response.data[1])
        self.assertFalse('memos' in response.data[2])

        # Log in as the advisor and make sure I see all three events.
        self.client.force_authenticate(user=Fixture1.advisor1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['memos'], ['A memo for e1'])
        self.assertEqual(response.data[1]['memos'], ['A memo for e2'])
        self.assertFalse('memos' in response.data[2])

    def test_performance_history_empty(self):
        url = '/api/v1/goals/{}/performance-history'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_performance_history(self):
        prices = (
            (Fixture1.fund1(), '20160101', 10),
            (Fixture1.fund1(), '20160102', 10.5),
            (Fixture1.fund1(), '20160103', 10.6),
            (Fixture1.fund1(), '20160104', 10.3),
            (Fixture1.fund1(), '20160105', 10.1),
            (Fixture1.fund1(), '20160106', 9.9),
            (Fixture1.fund1(), '20160107', 10.5),
            (Fixture1.fund2(), '20160101', 50),
            (Fixture1.fund2(), '20160102', 51),
            (Fixture1.fund2(), '20160103', 53),
            (Fixture1.fund2(), '20160104', 53.5),
            (Fixture1.fund2(), '20160105', 51),
            (Fixture1.fund2(), '20160106', 52),
            (Fixture1.fund2(), '20160107', 51.5),
        )
        Fixture1.set_prices(prices)

        order_details = (
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
        )
        orders = Fixture1.add_orders(order_details)

        execution_details = (
            (Fixture1.fund1(), orders[0], 3, 10.51, -75, '20160102'),
            (Fixture1.fund1(), orders[0], 4, 10.515, -75.05, '20160102'),
            (Fixture1.fund1(), orders[1], -1, 10.29, 10, '20160104'),
            (Fixture1.fund2(), orders[2], 2, 53.49, -110, '20160104'),
            (Fixture1.fund2(), orders[2], 8, 53.5, -430, '20160104'),
            (Fixture1.fund1(), orders[3], -3, 10.05, 30, '20160105'),
            (Fixture1.fund2(), orders[4], -3, 50.05, 145, '20160105'),
            (Fixture1.fund2(), orders[4], -2, 50.04, 98, '20160105'),
            (Fixture1.fund2(), orders[5], -5, 52, 255, '20160106'),
        )
        executions = Fixture1.add_executions(execution_details)

        # We distribute the entire executions to one goal.
        distributions = (
            (executions[0], 3, Fixture1.goal1()),
            (executions[1], 4, Fixture1.goal1()),
            (executions[2], -1, Fixture1.goal1()),
            (executions[3], 2, Fixture1.goal1()),
            (executions[4], 8, Fixture1.goal1()),
            (executions[5], -3, Fixture1.goal1()),
            (executions[6], -3, Fixture1.goal1()),
            (executions[7], -2, Fixture1.goal1()),
            (executions[8], -5, Fixture1.goal1()),
        )
        Fixture1.add_execution_distributions(distributions)

        url = '/api/v1/goals/{}/performance-history'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0], (16802, 0))  # 20160102
        self.assertEqual(response.data[1], (16803, Decimal('0.009524')))
        self.assertEqual(response.data[2], (16804, Decimal('-0.028302')))
        self.assertEqual(response.data[3], (16805, Decimal('-0.043901')))
        self.assertEqual(response.data[4], (16806, Decimal('-0.019802')))
        self.assertEqual(response.data[5], (16807, Decimal('0.060606')))
        self.assertEqual(response.data[6], (16808, 0))

    def test_put_settings_no_memo(self):
        # Test PUT with no memo
        old_events = Log.objects.count()
        old_memos = EventMemo.objects.count()
        url = '/api/v1/goals/{}/selected-settings'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        settings_changes = {"target": 1928355}
        response = self.client.put(url, settings_changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Make sure an event log was written
        self.assertEqual(old_events + 1, Log.objects.count())
        # Make sure no event memo was written
        self.assertEqual(old_memos, EventMemo.objects.count())

    def test_put_settings_with_memo_no_staff(self):
        # Test with a memo but no staff
        old_events = Log.objects.count()
        old_memos = EventMemo.objects.count()
        url = '/api/v1/goals/{}/selected-settings'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        settings_changes = {
            "target": 1928355,
            "event_memo": "Changed the target because I took an arrow to the knee."
        }
        response = self.client.put(url, settings_changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Make sure an event log was written
        self.assertEqual(old_events + 1, Log.objects.count())
        # Make sure an event memo was written
        self.assertEqual(old_memos + 1, EventMemo.objects.count())
        # Make sure the memo was the text I passed, and the default for staff is false.
        memo = EventMemo.objects.order_by('-id')[0]
        self.assertFalse(memo.staff)
        self.assertEqual(memo.comment, settings_changes['event_memo'])

    def test_put_settings_with_memo_true_staff(self):
        # Test with a memo and true staff
        old_events = Log.objects.count()
        old_memos = EventMemo.objects.count()
        url = '/api/v1/goals/{}/selected-settings'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        settings_changes = {
            "target": 1928355,
            "event_memo": "Changed the target because I took an arrow to the knee.",
            "event_memo_staff": True,
        }
        response = self.client.put(url, settings_changes)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Make sure an event log was written
        self.assertEqual(old_events + 1, Log.objects.count())
        # Make sure an event memo was written
        self.assertEqual(old_memos + 1, EventMemo.objects.count())
        # Make sure the memo was the text I passed, and staff is true.
        memo = EventMemo.objects.order_by('-id')[0]
        self.assertTrue(memo.staff)
        self.assertEqual(memo.comment, settings_changes['event_memo'])

    def test_post_settings_with_memo_false_staff(self):
        # Test POST with a memo and false staff
        old_events = Log.objects.count()
        old_memos = EventMemo.objects.count()
        url = '/api/v1/goals/{}/selected-settings'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        new_settings = {
            "completion": "2016-01-01",
            # Any metrics set must have a risk score metric.
            "metric_group": {"metrics": [self.risk_score_metric]},
            "hedge_fx": False,
            "event_memo": "Replaced because the old one smelled.",
            "event_memo_staff": False,
        }
        response = self.client.post(url, new_settings)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Make sure an event log was written
        self.assertEqual(old_events + 1, Log.objects.count())
        # Make sure an event memo was written
        self.assertEqual(old_memos + 1, EventMemo.objects.count())
        # Make sure the memo was the text I passed, and staff is false.
        memo = EventMemo.objects.order_by('-id')[0]
        self.assertFalse(memo.staff)
        self.assertEqual(memo.comment, new_settings['event_memo'])

    def test_put_settings_with_risk_too_high(self):
        url = '/api/v1/goals/{}/selected-settings'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        rsm = self.risk_score_metric.copy()
        rsm['configured_val'] = 0.9
        new_settings = {
            "metric_group": {"metrics": [rsm]},
        }
        self.assertLess(max_risk(Fixture1.goal1().selected_settings), 0.9)
        response = self.client.put(url, new_settings)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pending_transfers(self):
        # Populate an executed deposit and make sure no pending transfers are returned
        tx1 = Fixture1.transaction1()
        url = '/api/v1/goals/{}/pending-transfers'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # Populate 2 pending transfers (a deposit and withdrawal) and make sure they are both returned.
        tx2 = Fixture1.pending_deposit1()
        tx3 = Fixture1.pending_withdrawal1()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = [
            {
                "id": 3,
                "time": 946652400,
                "amount": -3500.0
            },
            {
                "id": 2,
                "time": 946648800,
                "amount": 4000.0
            }
        ]
        self.assertEqual(response.data, data)

    def test_recommended_risk_scores(self):
        """
        expects the years parameter for the span of risk scores
        """
        url = '/api/v1/goals/{}/risk-score-data'.format(Fixture1.goal1().id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['max'], 0.5)
        self.assertEqual(response.data['recommended'], 0.5)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calculate_all_portfolios(self):
        """
        expects the setting parameter to be a json dump
        of the goal settings to use for the portfolio calculation
        """
        # tickers for testing portfolio calculations in goals endpoint
        # otherwise, No valid instruments found
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())

        account = ClientAccountFactory.create(primary_owner=Fixture1.client1())
        # setup some inclusive goal settings
        goal_settings = GoalSettingFactory.create()
        # Create a risk score metric for the settings
        goal_metric = GoalMetricFactory.create(group=goal_settings.metric_group)
        goal = GoalFactory.create(account=account, active_settings=goal_settings, portfolio_set=self.portfolio_set)
        serializer = GoalSettingSerializer(goal_settings)
        url = '/api/v1/goals/{}/calculate-all-portfolios?setting={}'.format(goal.id, json.dumps(serializer.data))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calculate_portfolio(self):
        """
        expects the setting parameter to be a json dump
        of the goal settings to use for the portfolio calculation
        """
        # tickers for testing portfolio calculations in goals endpoint
        # otherwise, No valid instruments found
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())

        account = ClientAccountFactory.create(primary_owner=Fixture1.client1())
        # setup some inclusive goal settings
        goal_settings = GoalSettingFactory.create()
        # Create a risk score metric for the settings
        goal_metric = GoalMetricFactory.create(group=goal_settings.metric_group)
        goal = GoalFactory.create(account=account, active_settings=goal_settings, portfolio_set=self.portfolio_set)
        serializer = GoalSettingSerializer(goal_settings)
        url = '/api/v1/goals/{}/calculate-portfolio?setting={}'.format(goal.id, json.dumps(serializer.data))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calculate_portfolio_complete(self):
        # tickers for testing portfolio calculations in goals endpoint
        # otherwise, No valid instruments found
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())

        account = ClientAccountFactory.create(primary_owner=Fixture1.client1())
        # setup some inclusive goal settings
        goal_settings = GoalSettingFactory.create()
        # Create a risk score metric for the settings
        goal_metric = GoalMetricFactory.create(group=goal_settings.metric_group)
        goal = GoalFactory.create(account=account, active_settings=goal_settings, portfolio_set=self.portfolio_set)
        goal_settings.completion_date = timezone.now().date() - timedelta(days=365)
        serializer = GoalSettingSerializer(goal_settings)
        url = '/api/v1/goals/{}/calculate-all-portfolios?setting={}'.format(goal.id, json.dumps(serializer.data))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_add_goal_0_target(self):
        # tickers for testing portfolio calculations in goals endpoint
        # otherwise, No valid instruments found
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())

        url = '/api/v1/goals'
        self.client.force_authenticate(user=Fixture1.client1().user)
        account = ClientAccountFactory.create(primary_owner=Fixture1.client1())
        goal_settings = GoalSettingFactory.create()
        goal_metric = GoalMetricFactory.create(group=goal_settings.metric_group)
        ser = GoalCreateSerializer(data={
            'account': account.id,
            'name': 'Zero Goal Target',
            'type': GoalTypeFactory().id,
            'target': 0,
            'completion': timezone.now().date() + timedelta(days=7),
            'initial_deposit': 0,
            'ethical': True,
        })
        self.assertEqual(ser.is_valid(), True, msg="Serializer has errors %s"%ser.errors)
        response = self.client.post(url, ser.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['selected_settings']['target'], 0)
        self.assertEqual(response.data['on_track'], True)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_add_goal_complete(self):
        # tickers for testing portfolio calculations in goals endpoint
        # otherwise, No valid instruments found
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())

        url = '/api/v1/goals'
        self.client.force_authenticate(user=Fixture1.client1().user)
        account = ClientAccountFactory.create(primary_owner=Fixture1.client1())
        goal_settings = GoalSettingFactory.create()
        goal_metric = GoalMetricFactory.create(group=goal_settings.metric_group)
        ser = GoalCreateSerializer(data={
            'account': account.id,
            'name': 'Zero Goal Target',
            'type': GoalTypeFactory().id,
            'target': 500,
            'completion': timezone.now().date(),
            'initial_deposit': 0,
            'ethical': True,
        })
        self.assertEqual(ser.is_valid(), True, msg="Serializer has errors %s"%ser.errors)
        response = self.client.post(url, ser.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['selected_settings']['target'], 500)
        # "OnTrack" is false because the 500 deposit is still pending
        self.assertEqual(response.data['on_track'], False)

        goal = Goal.objects.get(pk=response.data['id'])
        goal.cash_balance += 500
        goal.save()

        response = self.client.get('%s/%s'%(url, goal.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['selected_settings']['target'], 500)
        self.assertEqual(response.data['on_track'], True)

    def test_sum_stocks_for_goal(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        fund1 = TickerFactory.create(asset_class=self.stocks_asset_class,
                                     benchmark_content_type=self.content_type,
                                     etf=True)
        goal = GoalFactory.create()

        order = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec = Execution.objects.create(asset=fund1,
                                        volume=10,
                                        order=order,
                                        price=2,
                                        executed=date(2014, 6, 1),
                                        amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist = ExecutionDistribution.objects.create(execution=exec, transaction=t1, volume=10)
        PositionLotFactory(quantity=10, execution_distribution=dist)
        weight_stocks = goal.stock_balance
        weight_bonds = goal.bond_balance
        weight_core = goal.core_balance
        self.assertTrue(weight_stocks == 100)
        self.assertTrue(weight_bonds == 0)
        self.assertTrue(weight_core == 100)

    def test_get_positions_all(self):
        fund = TickerFactory.create(unit_price=2.1)
        fund2 = TickerFactory.create(unit_price=4)
        goal = GoalFactory.create()
        today = date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order1 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec1 = Execution.objects.create(asset=fund,
                                         volume=10,
                                         order=order1,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist1 = ExecutionDistribution.objects.create(execution=exec1, transaction=t1, volume=10)
        PositionLotFactory(quantity=10, execution_distribution=dist1)

        order2 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec2 = Execution.objects.create(asset=fund,
                                         volume=5,
                                         order=order2,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=10)
        t2 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=10)
        dist2 = ExecutionDistribution.objects.create(execution=exec2, transaction=t2, volume=5)
        PositionLotFactory(quantity=5, execution_distribution=dist2)

        order3 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec3 = Execution.objects.create(asset=fund2,
                                         volume=1,
                                         order=order3,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=4)
        t3 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=4)
        dist3 = ExecutionDistribution.objects.create(execution=exec3, transaction=t3, volume=1)
        PositionLotFactory(quantity=1, execution_distribution=dist3)

        positions = goal.get_positions_all()

        self.assertTrue(positions[0]['quantity'] == 15)
        self.assertTrue(positions[1]['quantity'] == 1)

    def test_get_goal_positions(self):
        client = Fixture1.client1()
        account = ClientAccountFactory.create(primary_owner=client)
        goal = GoalFactory.create(account=account)
        url = '/api/v1/goals/{}/positions'.format(goal.pk)
        self.client.force_authenticate(client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Goal positions endpoint returns ok for Goal with no positions')
        # add a position
        # lots = PositionLot.objects.filter(quantity__gt=0).filter(execution_distribution__transaction__from_goal=self).\
        #     annotate(ticker_id=F('execution_distribution__execution__asset__id'),
        #              price=F('execution_distribution__execution__asset__unit_price'))\
        #     .values('ticker_id', 'price').annotate(quantity=Sum('quantity'))
        fund = TickerFactory.create(unit_price=2.1)
        fund2 = TickerFactory.create(unit_price=4)
        today = date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order1 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec1 = Execution.objects.create(asset=fund,
                                         volume=10,
                                         order=order1,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist1 = ExecutionDistribution.objects.create(execution=exec1, transaction=t1, volume=10)
        PositionLotFactory(quantity=10, execution_distribution=dist1)

        order2 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec2 = Execution.objects.create(asset=fund,
                                         volume=5,
                                         order=order2,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=10)
        t2 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=10)
        dist2 = ExecutionDistribution.objects.create(execution=exec2, transaction=t2, volume=5)
        PositionLotFactory(quantity=5, execution_distribution=dist2)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Goal positions endpoint returns ok for Goal with positions')
