import logging
from itertools import chain

import pandas as pd
from django.db import transaction
from django.utils import timezone

from api.v1.goals.serializers import GoalSettingStatelessSerializer, GoalSettingSerializer
from main.models import GoalMetricGroup, GoalSetting, Portfolio, PortfolioItem, Ticker, GoalMetric
from portfolios.calculation import calculate_portfolio, get_instruments
from portfolios.providers.data.django import DataProviderDjango
from portfolios.providers.execution.django import ExecutionProviderDjango
from retiresmartz.calculator.assets import TaxDeferredAccount
from retiresmartz.calculator.base import DesiredCashFlow
from .assets import Asset, TaxPaidAccount
from .cashflows import CashFlow

logger = logging.getLogger('retiresmartz.calculator')


@transaction.atomic
def create_settings(plan):
    """
    Creates some settings that can be used to create a real retirement goal if desired.
    :param plan: The retirement plan to create settings for.
    :return: A GoalSetting object that has been saved in the database.
             The caller needs to destroy it if it is no longer required
    :raises Unsatisfiable if no suitable portfolio could be found for the plan.
    """
    metric_group = GoalMetricGroup.objects.create(type=GoalMetricGroup.TYPE_CUSTOM)
    settings = GoalSetting.objects.create(
        target=0,
        completion=timezone.now().date(),
        hedge_fx=False,
        metric_group=metric_group,
    )

    risk_metric = GoalMetric.objects.create(group=metric_group,
                                            type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                            comparison=GoalMetric.METRIC_COMPARISON_EXACTLY,
                                            rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                            rebalance_thr=0.05,
                                            configured_val=plan.desired_risk)

    # Create a mock goal so we can call calculate_portfolio
    class MockGoal(object):
        portfolio_set = plan.client.advisor.default_portfolio_set
        id = 0
        available_balance = 100000
        current_balance = 100000

        def __str__(self):
            return "Retiresmartz calculation Goal for plan: {}".format(plan)

    # Create a dummy settings object for the calculation.
    # We need to do this because we are using a fake goal, as we don't have a real goal yet.
    settings_data = GoalSettingSerializer(instance=settings).data
    calc_settings = GoalSettingStatelessSerializer.create_stateless(settings_data, MockGoal())

    data_provider = DataProviderDjango()
    idata = get_instruments(data_provider)

    weights, er, stdev = calculate_portfolio(
        settings=calc_settings,
        idata=idata,
        data_provider=data_provider,
        execution_provider=ExecutionProviderDjango()
    )

    portfolio = Portfolio.objects.create(
        setting=settings,
        stdev=stdev,
        er=er,
    )
    items = [PortfolioItem(portfolio=portfolio,
                           asset=Ticker.objects.get(id=tid),
                           weight=weight,
                           volatility=idata[0].loc[tid, tid])
             for tid, weight in weights.items()]
    PortfolioItem.objects.bulk_create(items)

    return settings


class Calculator(object):
    def __init__(self, cash_flows: [CashFlow], assets: [Asset]):
        """
        :param cash_flows: A list of cash flow providers. Will be requested for a cash flow every month.
        :param assets: A list of assets. Will be withdrawn from in order to try and make up a desired cash flow.
        """
        self._cash_flows = cash_flows
        self._assets = assets

    def calculate(self, desired_cash_flow_calculator: DesiredCashFlow) -> (pd.DataFrame, pd.DataFrame):
        """
        - desired_cash_flow_calculator is a generator object that yields a
        (date, amount) tuple.

        - asset_values is a pandas dataframe with index being the dates yielded
        by the desired_cash_flow_calculator, columns are each of the assets,
        labelled with the asset name.

        - income_values is a pandas dataframe with index being the dates yielded
        by the desired_cash_flow_calculator, two cash flow columns. First is
        'desired', second is 'actual'

        calculate() resets the assets and cash_flow_providers, then iteratively
        yields a value from the desired_cash_flow_calculator, then requests all
        income for the date, then withdraws from the assets in order until the
        desired_cash_flow is achieved.

        :return: asset_values, income_values
        """
        [fr.reset() for fr in chain(self._cash_flows, self._assets)]

        asset_values = pd.DataFrame(columns=[a.name for a in self._assets])
        income_values = pd.DataFrame(columns=['desired', 'actual'])

        for date, desired_amount in desired_cash_flow_calculator:
            cf_amount_total = 0
            for cf in self._cash_flows:
                cf_amount = cf.on(date)
                cf_amount_total += cf_amount

            amount_needed = desired_amount - cf_amount_total
            asset_value = [0] * len(self._assets)
            for i, a in enumerate(self._assets):
                if amount_needed > 0:
                    value = a.withdraw(date, amount_needed)
                    amount_needed -= value
                asset_value[i] = a.balance(date)

            asset_values.loc[date] = asset_value
            income_values.loc[date] = [desired_amount, desired_amount - amount_needed]

        return asset_values, income_values
