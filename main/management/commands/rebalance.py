'''
 - Conversion from cash to funds happens when the TCR of all proposed changes, including investing the cash amount in a
   goal is less than the ATCS.

'''

'''
Transaction Cost Ratio (TCR)
    - The ratio of the size of the transaction vs the costs involved.

Automatic Transaction Cost Threshold (ATCS)
    - The limit of TCR, below which an automatic transaction will not be performed.

Deciding when to rebalance:
 - A user can decide to "Rebalance Now". If the "Rebalance now" button is pressed. Make sure we display to the user
   what the estimated cost of the rebalance is and how it compares to the ATCS.

How to rebalance:
    - If the active metrics are different from the approved metrics, simply apply the approved portfolio. Otherwise,
      - If we have available funds, run the "Add funds" routine (adding appropriate constraints so there can be no removals from assets)
        - Otherwise assume unsatisfiable
      while (we get an unsatisfiable optimisation)
        - If there is drift is due to portfolio mix metric:
            - Remove units from the most overweight asset (or the asset that has moved the most in the most overweight asset
              group) in each drifted feature since the last rebalance (the Active Settings),
              to establish it's desired weight in the portfolio.
            - Run the "Add funds" routine (adding appropriate constraints so there can be no removals from other assets)
        - If the portfolio is unsatifiable and there is drift is due to risk:
          - If the current risk is higher:
            - remove units from assets that have increased in volatility*weight against the active portfolio,
              starting with the most overweight by mix if such constraints are set, otherwise, starting with highest volatility_weight
            - Run the "Add funds" routine (adding appropriate constraints so there can be no removals from other assets)
          - If the current risk is lower:
            - remove units from assets that have decreased in volatility*weight against the active portfolio,
              starting with the most overweight by mix if such constraints are set, otherwise, starting with lowest volatility_weight
        - Run the "Add funds" routine (adding appropriate constraints so there can be no removals from other assets)
        - keep going until risk is back to it's set level
        - keep going until we get a satisfiable portfolio



Confirming the rebalance.
 - Within overnight process, run all processes for an account, then if ATCS is not met, don't send to market.
    - This means if we're automatically rebalancing and the TCR for the rebalance is greater than the ATCS, delay the rebalance.
 - Once the nightly process is done, compare the markowitz cost of the resulting portfolio against the daily optimum
   for this goal. If it's over some percent different, inform the Client and Advisor that the portfolio needs to be
   reoptimised.
 - Depending if the customer is fully managed or not, we may need to confirm the rebalance. Actually, confirming
   rebalances should be a selectable feature per account either way.


'''