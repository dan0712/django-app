from datetime import timedelta

import numpy as np
from django_pandas.io import read_frame

from common.constants import WEEKDAYS_PER_YEAR
from portfolios.exceptions import OptimizationException
from portfolios.returns import get_return_history, get_benchmark_returns, filter_returns

# TODO: Once we have automated predictions, reduce this value.
OLDEST_ACCEPTABLE_DATA = 180  # The number of days back we will look data before we consider it too old.

MAX_HISTORY = 20  # The maximum years of history we want to use
CYCLE_LABEL = 'CYCLE'


class InvestmentClock(object):

    def __init__(self, data_provider):
        self.data_provider = data_provider

    def get_last_cycle_start(self):
        """
        Get the beginning of the last complete investment cycle in our history.
        :return: The date of the first day of the last complete investment cycle.
        """
        obs = self.data_provider.get_investment_cycles()
        # Populate the cache as we'll be hitting it a few times. Boolean evaluation causes full cache population
        if not obs:
            raise OptimizationException("There are no historic observations available")

        # Get the investment cycle for the current date
        current_cycle = obs.last().cycle

        # Get the end date of the last non-current cycle before the current one
        pre_dt = obs.exclude(cycle=current_cycle).last().as_of

        # Get the end date of the previous time the current cycle was
        pre_on_dt = obs.filter(as_of__lt=pre_dt).filter(cycle=current_cycle).last().as_of

        # Get the end date of the time before that when we were not in the current cycle
        pre_off_dt = obs.filter(as_of__lt=pre_on_dt).exclude(cycle=current_cycle).last().as_of

        # Not get the first date after this when the current cycle was on and we have the answer
        return obs.filter(as_of__gt=pre_off_dt).first().as_of

    def get_fund_predictions(self):
        """
        This method generates 12 month predictions for fund expected returns and covariance.
        :return: (ers, covars)
                 ers is a pandas series of 12 month expected return indexed on fund id
                 covars is a pandas dataframe of 12 month expected covariance indexed on both axis by fund id
        """

        today = self.data_provider.get_current_date()

        # The earliest data we want to build our predictions
        begin_date = today - timedelta(days=365 * MAX_HISTORY)

        # Get the funds
        funds = self.data_provider.get_tickers()

        # Get all the return data relating to the funds
        fund_returns, benchmark_returns = get_return_history(funds, begin_date, today)

        # For now we're assigning the benchmark returns for the return history.
        returns = get_benchmark_returns(funds, benchmark_returns)

        # Filter any funds that don't have enough data.
        # Our latest start date is the first day of the last complete investment cycle from the current date.
        latest_start = self.get_last_cycle_start()
        returns = filter_returns(returns, OLDEST_ACCEPTABLE_DATA, latest_start=latest_start)

        oldest_dt = today - timedelta(days=OLDEST_ACCEPTABLE_DATA)
        cycles = self.get_cycle_obs(begin_date)
        if cycles.index[-1] < oldest_dt:
            raise OptimizationException('Last observed cycle was too long ago')

        probs = np.array(self.get_normalized_probabilities(oldest_dt).tail(1))

        return_cycles = self._merge_cycle_returns(returns, cycles)
        mu = (1 + self._expected_returns_prob_v1(return_cycles, probs)) ** WEEKDAYS_PER_YEAR - 1
        sigma = self._covariance_matrix_prob_v1(return_cycles, probs) * WEEKDAYS_PER_YEAR
        return mu, sigma

    def get_cycle_obs(self, begin_date):
        """
        Returns a pandas timeseries dataframe with the cycle id as the value.
        :param begin_date: The earliest date you want the series from.
        :return:
        """
        qs = self.data_provider.get_investment_cycles().filter(as_of__gt=begin_date)
        return read_frame(qs, fieldnames=['cycle'], index_col='as_of', verbose=False)['cycle']

    def get_normalized_probabilities(self, begin_date):
        """
        Normalize the probability to sum 1 (This will configure a prob space)
        :param begin_date: The earliest date you want the probabilities from
        :return: Dataframe of normalized probabilities.
                 The fields are in positions corresponding to the class ids on InvestmentCycleObservation.
        """
        qs = self.data_provider.get_investment_cycle_predictions().filter(as_of__gt=begin_date)
        probs_df = read_frame(qs,
                              fieldnames=['eq', 'eq_pk', 'pk_eq', 'eq_pit', 'pit_eq'],
                              index_col='as_of')
        if probs_df.empty:
            raise OptimizationException("There are no investment clock predictions available")
        sum_row = probs_df.sum(axis=1)
        norm_probs = probs_df.div(sum_row, axis=0)
        return norm_probs

    def _merge_cycle_returns(self, returns, cycles):
        """
        Merge a Daily and a Monthly Dataframe by certain label column
        :param returns: The Dataframe of the daily return observations
        :param cycles: The Dataframe of the monthly investment cycle observations
        :return: Returns the merged dataframe
        """
        returns[CYCLE_LABEL] = cycles.reindex(returns.index, method='pad')
        if len(returns[CYCLE_LABEL].unique()) != 5:
            raise OptimizationException("All investment cycles were not represented in data.")
        return returns

    def _expected_returns_prob_v1(self, merged_df, prob_vector):
        """
        Calculate the ER Vector by prob weighting the ER by stage.
        :param merged_df: The Dataframe of Returns with Label Column
        :param prob_vector: A 1x5 numpy array of the probabilities of each investment cycle.
        :return: Expected Return Vector as a pandas series, index Ticker id
        """
        summary_df = merged_df.groupby(CYCLE_LABEL, as_index=True).mean().T
        expected_return = summary_df.dot(prob_vector.T)
        return expected_return[0]

    def _covariance_matrix_prob_v1(self, merged_df, prob_vector):
        """
        Calculate the Cov Matrix by prob weighting the Cov by Stage.
        :param merged_df: The Dataframe of Returns with Label Column
        :param prob_vector: A 1x5 numpy array of the probabilities of each investment cycle.
                            The position MUST match the CYCLE label at that position.
        :return: Expected Cov Matrix
        """
        total_cov = merged_df.groupby(CYCLE_LABEL, as_index=True).cov()
        cov_matrix = 0
        for i in range(5):
            cov_matrix += total_cov.loc[i, :] * prob_vector[:, i]
        return cov_matrix
