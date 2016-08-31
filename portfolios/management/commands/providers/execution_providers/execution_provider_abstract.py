from abc import ABC, abstractmethod
from common.structures import ChoiceEnum
import pandas as pd

class Reason(ChoiceEnum):
    DRIFT = 0  # The Request was made to neutralise drift on the goal
    WITHDRAWAL = 1  # The request was made because a withdrawal was requested from the goal.
    DEPOSIT = 2  # The request was made because a deposit was made to the goal
    METRIC_CHANGE = 3  # The request was made because the inputs to the optimiser were changed.


class State(ChoiceEnum):
    PENDING = 0  # Raised somehow, but not yet approved to send to market
    APPROVED = 1  # Approved to send to market, but not yet sent.
    SENT = 2  # Sent to the broker (at least partially outstanding).
    CANCEL_PENDING = 3  # Sent, but have also sent a cancel
    COMPLETE = 4  # May be fully or partially executed, but there is none left outstanding.


class ExecutionProviderAbstract(ABC):

    @abstractmethod
    def get_execution_request(self, reason):
        pass

    @abstractmethod
    def create_market_order(self, account):
        pass

    @abstractmethod
    def create_execution_request(self, reason, goal, asset, volume, order, limit_price):
        pass

    @staticmethod
    def _construct_matrix(attribute, executions):
        executions_per_ticker = dict()
        for execution in executions:
            if execution.asset.id not in executions_per_ticker:
                executions_per_ticker[execution.asset.id] = dict()
            executions_per_ticker[execution.asset.id][execution.executed] = getattr(execution, attribute)

        transactions = pd.DataFrame()
        for key, value in executions_per_ticker.items():
            ticker = pd.DataFrame.from_dict(value, orient='index')
            ticker.index = pd.to_datetime(ticker.index)
            ticker = ticker.sort_index()
            ticker.columns = [key]
            transactions = pd.concat([transactions, ticker], axis=1)
        return transactions






