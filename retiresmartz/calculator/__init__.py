from itertools import chain

from pandas.core.frame import DataFrame

from retiresmartz.calculator.assets import TaxDeferredAccount
from retiresmartz.calculator.base import DesiredCashFlow
from .assets import Asset, TaxPaidAccount
from .cashflows import CashFlow


class Calculator(object):
    def __init__(self, birthday):
        self.birthday = birthday
        self._cash_flows = []
        self._assets = []

    def add_cash_flows(self, *cash_flows: [CashFlow]) -> None:
        """
        Adds a cash flow provider to the calculator. Order of addition not important.
        """
        self._cash_flows.extend(cash_flows)

    def add_assets(self, *assets: [Asset]) -> None:
        """
        Adds a financial asset to the list of assets. Kept in order of addition.
        """
        self._assets.extend(assets)

    def calculate(self, desired_cash_flow_calculator: DesiredCashFlow) -> (DataFrame, DataFrame):
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

        asset_values = DataFrame(columns=[a.name for a in self._assets])
        income_values = DataFrame(columns=['desired', 'actual'])

        for date, desired_amount in desired_cash_flow_calculator:
            cf_amount_total = 0
            for cf in self._cash_flows:
                cf_amount = cf.on(date)
                cf_amount_total += cf_amount

            amount_needed = desired_amount - cf_amount_total
            asset_value = [0] * len(self._assets)
            for i, a in enumerate(self._assets):
                if amount_needed <= 0:
                    break
                if a.available_after is None or a.available_after >= date:
                    value = a.withdraw(date, amount_needed)
                    asset_value[i] = a.balance()
                    amount_needed -= value

            asset_values.loc[date] = asset_value
            income_values.loc[date] = [desired_amount, desired_amount - amount_needed]

        return asset_values, income_values
