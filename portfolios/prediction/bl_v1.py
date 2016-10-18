import logging
from collections import defaultdict
import itertools

import pandas as pd
import numpy as np

from portfolios.algorithms.bl import bl_model
from portfolios.algorithms.covar import lw_covars

logger = logging.getLogger("portfolios.prediction.bl_v1")


def get_covars_v2(returns, benchmarks, benchmark_map):
    """
    Calculates a constrained covariance matrix.
    :param returns: A pandas dataframe of the covariance between the funds and benchmarks.
    :param benchmarks: How many benchmarks are there?
    :param benchmark_map: Map from fund id to benchmark id.
    :return: A covariance matrix suitable for use in Black-Litterman calculations.
    """
    TE = pd.DataFrame({f: (returns[f] - returns[i]) for f, i in benchmark_map.items()}, index=returns.index)
    TE = TE.reindex(index=TE.index, columns=returns.columns[benchmarks:])

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("TE as table: {}".format(TE.to_dict('list')))

    # This is the covariance matrix for all the funds' tracking errors
    te_cov = lw_covars(TE)

    # Build the related fund tracking error covariance matrix. (Zero out funds not sharing same index)
    te_cov_rel = pd.DataFrame(np.zeros(te_cov.shape), index=te_cov.index, columns=te_cov.columns)
    index_to_fund = defaultdict(list)
    for f, i in benchmark_map.items():
        index_to_fund[i].append(f)
    for rfs in index_to_fund.values():
        for r, c in itertools.product(rfs, repeat=2):
            te_cov_rel.loc[r, c] = te_cov.loc[r, c]

    # Build the P matrix
    P = pd.DataFrame(np.zeros((benchmarks, len(te_cov))),
                     index=returns.columns[:benchmarks],
                     columns=returns.columns[benchmarks:])
    for f, i in benchmark_map.items():
        P.loc[i, f] = 1

    # Build the cov(I,I) matrix
    sig_ii = lw_covars(returns.iloc[:, :benchmarks])

    # Put the full martrix together and return it.
    mu_covars_l = pd.concat([sig_ii, P.T.dot(sig_ii)])
    mu_covars_r = pd.concat([sig_ii.dot(P), P.T.dot(sig_ii).dot(P) + te_cov_rel])
    return pd.concat([mu_covars_l, mu_covars_r], axis=1)


def get_views(portfolio_set, instruments):
    """
    Return the views that are appropriate for a given portfolio set.
    :param portfolio_set: The portfolio set to get the views for. May be null, in which case no views are returned.
    :param instruments: The n x d pandas dataframe with n instruments and their d data columns.
    :return: (views, view_rets)
        - views is a masked nxm numpy array corresponding to m investor views on future asset movements
        - view_rets is a mx1 numpy array of expected returns corresponding to views.
    """
    # TODO: We should get the cached views per portfolio set from redis

    if portfolio_set is None:
        ps_views = []
        logger.warn("No portfolio_set passed to get_views, no views can therefore be found.")
    else:
        ps_views = portfolio_set.get_views_all()

    views = np.zeros((len(ps_views), instruments.shape[0]))
    qs = []
    masked_views = []
    for vi, view in enumerate(ps_views):
        header, view_values = view.assets.splitlines()

        header = header.split(",")
        view_values = view_values.split(",")

        for sym, val in zip(header, view_values):
            _symbol = sym.strip()
            try:
                si = instruments.index.get_loc(_symbol)
                views[vi][si] = float(val)
            except KeyError:
                mstr = "Ignoring view: {} in portfolio set: {} as symbol: {} is not active"
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(mstr.format(vi, portfolio_set.name, _symbol))
                masked_views.append(vi)
        qs.append(view.q)

    views = np.delete(views, masked_views, 0)
    qs = np.delete(np.asarray(qs), masked_views, 0)
    return views, qs


def get_market_weights(instruments):
    """
    Get a set of initial weights based on relative market capitalisation
    :param instruments: The instruments table
    :return: A pandas series indexed as the instruments table containing the initial unoptimised instrument weights.
    """
    interested = instruments['mkt_cap']
    total_market = interested.sum()
    if total_market == 0:
        return pd.Series([0]*len(interested), index=interested.index)
    return interested / total_market


def run_bl(instruments, covars, target_instruments, samples, portfolio_set):
    """
    Runs Black-Litterman to determine ers and weights of funds based on benchmarks and fund views
    :param instruments: The table of instrument data for funds and their benchmarks
    :param covars: The covariance matrix for funds and their benchmarks
    :param target_instruments: The fund instruments from the main instruments table that we are interested in.
    :param samples: The number of samples used to create the covariance matrix
    :param portfolio_set: The portfolio set that specifies the views. If None, no views will be used.
    :return: The mu and sigma for the funds only.
    """

    # Get the indexes for the benchmarks for each of the funds
    blabels = target_instruments['id'].unique() #we need benchmark, for now just use fund

    # Get all the benchmarks and fund instruments
    bl_instruments = instruments.loc[blabels.tolist() + target_instruments.index.tolist()]

    # Get the market weights for the benchmarks for each of the funds, and the funds.
    # The market caps for the funds should be zero.
    market_caps = get_market_weights(bl_instruments)

    # Get the views appropriate for the settings
    views, vers = get_views(portfolio_set, bl_instruments)

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.loc[bl_instruments['id'], bl_instruments['id']]
    mu, sigma = bl_model(lcovars.values,
                         market_caps.values,
                         views,
                         vers,
                         samples)

    if logger.level == logging.DEBUG:
        msg = "Ran BL with samples: {}, index: {}\ncovars:\n{}\nWeights:{}\nGot mu:\n{}\nsigma:\n{}"
        logger.debug(msg.format(
            samples,
            lcovars.index.tolist(),
            lcovars.values.tolist(),
            market_caps.values.tolist(),
            mu.tolist(),
            sigma.tolist())
        )

    # modify the mu and sigma to only be the funds, then return just those.
    return mu[len(blabels):], sigma[len(blabels):, len(blabels):]


