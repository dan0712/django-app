'''
Deciding when to rebalance:
 - A user can decide to "Rebalance Now". If the "Rebalance now" button is pressed. Make sure we display to the user
   what the estimated cost of the rebalance is and how it compares to the ATCS.
'''
from main.models import Position
from portfolios.management.commands.portfolio_calculation import optimize_settings, make_orderable


def optimise_up(weights):
    """
    Reoptimise the portfolio adding appropriate constraints so there can be no removals from assets
    ":param goal: The goal to
    :return: weights
    """


def get_weights(settings):
    return {item.asset.id: item.weight for item in settings.portfolio.items.all()}


def metrics_changed(goal):
    """
    Return true if the metrics contributing to the goal have changed between the active_settings and the
    approved_settings in any aspect that contributes to new optimal distribution.
    :param goal:
    :return: Boolean (True if changed)
    """
    return goal.active_settings.constraint_inputs() != goal.selected_settings.constraint_inputs()


def build_positions(new_weights):
    # Establish the positions required for the new weights.


    # Make sure we are no out of drift now we have made the weights orderable.


def create_request(goal, new_positions):
    """
    Create a MarketOrderRequest for the position changes that will take the existing positions to the new positions.
    :param goal:
    :param new_positions: A dict from asset id to position
    :return: A list of Execution Requests
    """

    requests = []
    # Get the existing positions
    for position in Position.objects.filter(goal=goal).all():




def perturbate(goal):
    """
    :param goal: The goal who's current holding we want to perturbate until we get a satisfiable set of constraints.
    :returns: The new weights to use for the goal's holdings that fit within the current constraints (0 drift).

    Perturbation strategy:
      - Optimise the portfolio adding appropriate constraints so there can be no removals from assets.
      while (we get an unsatisfiable optimisation (we have drift))
        - If there is drift is due to portfolio mix metric:
            - Remove units from the most overweight asset (or the asset that has moved the most in the most overweight asset
              group) in each drifted feature since the last rebalance (the Active Settings),
              to establish it's desired weight in the portfolio.
            - Optimise the portfolio adding appropriate constraints so there can be no removals from assets.
        - If there is drift is due to risk:
          - If the current risk is higher:
            - remove units from a single asset that have increased in volatility*weight against the active portfolio,
              starting with the most overweight by mix if such constraints are set, otherwise, starting with highest volatility_weight
          - If the current risk is lower:
            - remove units from a single asset that has decreased in volatility*weight against the active portfolio,
              starting with the most overweight by mix if such constraints are set, otherwise, starting with lowest volatility_weight
        - Optimise the portfolio adding appropriate constraints so there can be no removals from assets.
    """
    weights, cost = optimise_up(weights)


def rebalance(goal):
    """
    Rebalance Strategy:
    :param goal:
    :return:
    """

    # If our important metrics were changed, all attempts to perturbate the old holdings is avoided, and we simply
    # return the new desired weights. We don't try and return the previously optimised weights, as there may already be
    # drift, so we want to use the new optimised weights.
    if metrics_changed(goal):
        odata = optimize_settings(goal.approved_settings)
        weights, cost, xs, sigma, mu, lam, constraints, settings_instruments, _, _, _ = odata
        # WE don't do the alignment stage, as that will be done at the end of the daily process.
        weights, cost = make_orderable(weights,
                                       cost,
                                       xs,
                                       sigma,
                                       mu,
                                       lam,
                                       constraints,
                                       settings_instruments,
                                       goal.available_balance,
                                       settings_instruments['price'],
                                       align=True)
        return create_requests(goal, weights)

    # The important metrics weren't changed, so try and perturbate.
    weights = perturbate()


