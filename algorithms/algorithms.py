from main.management.commands import rebalance as rb

class FundSelectionAlgorithm(object):
    """
    This class is just a description of the interfaces that a Fund Selection Algorithm needs to have.
    """
    def filter(self, fund_data):
        """
        :param fund_data:
        :return: A list of instrument identifiers (api and id at that api) that should be currently active.
        """
        pass


class OptimisationAlgorithm(object):
    def optimise_portfolio(self, settings, idata):
        """
        Calculates the instrument weights to use for a given goal settings.
        :param settings: The settings to calculate the portfolio for.
        :param idata: The instrument data to use for the optimisation
        :return: (weights, er, variance) All values will be None if no suitable allocation can be found.
                 - weights: A Pandas series of weights for each instrument.
                 - er: Expected return of portfolio
                 - stdev: stdev of portfolio
        """

        pass


class RebalanceAlorithm(object):
    def rebalance(self, holdings, idata, settings):
        """
        :param holdings:
        :param idata:
        :return: A MarketOrderRequest and the list of associated ExecutionRequests
        """


class RiskAlgorithm(object):
    def calculate_bounds(self, idata):
        """
        Calculates the meaning of the range for the risk_score given updated instrument data
        :param idata:
        :return: None
        """

        pass

    def risk_score_to_cons(self, score):
        """
        Converts a risk score between 0 and 1 into some constants suitable for an optimisation and rebalance algorithm.
        That is, a Risk Algorithm must be suited to a Rebalance and Optimisation algorithm, as the constants produced
        by this method must be usable by and suitable for the Rebal/Optimise algos.
        :param score: A numeric real value between 0 and 1
        :return: An object representing the constants suitable for a matching Rebal and Opt algo.
        """
        pass


class ViewCreationAlgorithm(object):
    def create_views(self, idata):
        """
        :param idata:
        :return: (views, view_rets)
            - views is a masked nxm numpy array corresponding to m investor views on future asset movements
            - view_rets is a mx1 numpy array of expected returns corresponding to views.
        """
        pass

