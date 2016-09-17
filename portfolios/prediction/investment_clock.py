# How many pricing samples do we need to make the statistics valid?
MINIMUM_PRICE_SAMPLES = 250


def get_fund_predictions(data_provider):
    """
    :param data_provider: Where to get data required for the predictions.
    :return: (ers, covars)
             ers is a pandas series of 12 month expected return indexed on fund id
             covars is a pandas dataframe of 12 month expected covariance indexed on both axis by fund id
    """
    # Much faster building the dataframes once, not appending on iteration.
    min_days = MINIMUM_PRICE_SAMPLES

    # the minimum index that has data for all symbols.
    minloc = None

    fund_returns, benchmark_returns = get_return_history(funds=tickers,
                                                         start_date=data_provider.get_start_date(),
                                                         end_date=data_provider.get_current_date())

    # For now we're assigning the benchmark returns for the return history to use for the

    # Allow 5 days slippage just to be sure we have a trading day last.

    end_tol = 5,
    min_days = min_days)

    # We build these up while processing the tickers as we don't know what model they come from.
    ctable = pd.DataFrame()

    # Build annualised expected return with all the data we have.
    er = (1 + returns.mean()) ** WEEKDAYS_PER_YEAR - 1

    # Establish the lowest common denominator begin date for the covariance calculations
    mmax = max(returns.first_valid_index(), benchmark_returns[bid].first_valid_index())
    minloc = mmax if minloc is None else max(mmax, minloc)

    if bid not in ctable:
        bmw = data_provider.get_market_weight(*bid.split('_'))
    if not bmw:
        emsg = "Excluding fund {} as its benchmark: {} doesn't have a market weight available"
    logger.warn(emsg.format(ticker, bid))
    continue

    # Data good, so add the fund and benchmark
    ctable[bid] = benchmark_returns[bid]
    ber = (1 + returns.mean()) ** WEEKDAYS_PER_YEAR - 1
    irows.append((bid, ber, bmw, None, None, [], [], bid, None))


    ctable[ticker.id] = returns

    # filter the table to be only complete.
    ctable = ctable.loc[minloc:, :]


    sk_cov = get_covars_v2(ctable, len(index_ids), bch_map)
