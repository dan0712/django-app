import datetime

from django import test

from api.v1.tests.factories import GoalFactory, PositionFactory, TickerFactory, \
    TransactionFactory, GoalSettingFactory, GoalMetricFactory, AssetFeatureValueFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction
from portfolios.providers.execution.django import ExecutionProviderDjango
from main.management.commands.rebalance import perturbate_mix

from main.models import Ticker

class RebalanceTest(test.TestCase):
    def test_perturbate_mix(self):

        t1 = TickerFactory.create(symbol='SPY')
        t2 = TickerFactory.create(symbol='QQQ')
        t3 = TickerFactory.create(symbol='TLT')
        t4 = TickerFactory.create(symbol='IEF')
        equity = AssetFeatureValueFactory.create(assets=[t1, t2])
        bond = AssetFeatureValueFactory.create(assets=[t3, t4])

        goal_settings = GoalSettingFactory.create()

        GoalMetricFactory.create(group=goal_settings.metric_group, feature=equity)
        GoalMetricFactory.create(group=goal_settings.metric_group, feature=bond)

        goal = GoalFactory.create(active_settings=goal_settings)

        #t = Ticker.objects.get(symbol='TLT', features__name=bond)

        daco = perturbate_mix(goal, None)
        print('done')
