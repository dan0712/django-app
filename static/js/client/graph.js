function get_probabilistic_returns(z_score, er, stdev, periods) {
    // er is the expected return (usually somewhere around 1)
    val = 0
    // Output is the values for the end of the period.
    out = []
    for (period in periods) {
        mr = er + stdev * z_score
        // delta is the amount to add to the val at the start of the period
        val = (val + period.delta) * mr
        if (period.output) {
            out.push(val)
        }
    }


function get_return_periods(opening_balance, period_delta, periods, points) {
    // period_delta is raw value delta made per period (deposit minus any fixed fees per period)
    // points is the number of output points to include in the period series
    freq = periods / points
    last = 0
    out = [{delta: opening_balance, output: true}]
    for (i = 1; i < periods; ++i) {
        if (~~(i/freq) > last) {
            last = i
            output = true
        }
        else {
            output = false
        }
        out.push({delta: period_delta, output: output})
    }
    return out
}

// The number of points to have on the return chart
CHART_POINTS = 50

// Example use:
periods = get_return_periods(goal.available_balance,
                             goal.auto_deposit - goal.monthly_fees, (auto_deposit Comes from the AutomaticDeposit model, currently no monthly fees)
                             (goal.completion_date - today()).months(),
                             CHART_POINTS)


//lines we need on chart:

//Goal target
horizontal line got from goal.target

//raw invested
get_probabilistic_returns(0.0, 0.0, 0.0, periods)

// 2.5, 10, 50, 90 & 97.5% probability lines for current portfolio (only these need to be redrawn on risk slider move)
var z_scores = {
    z975Pct: 1.959964,
    z90Pct: 1.281552,
    z50Pct: 0,
    z10Pct: -1.281552,
    z225Pct: -1.959964
}
port_er = (1 + (portfolio.er / 100)) ** (1/12)
port_vol = (1 + (portfolio.volatility / 100)) ** (1/12)
for z_score in z_scores.values():
    data = get_probabilistic_returns(z_score, port_er, port_vol, periods)