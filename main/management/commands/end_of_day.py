'''

Transaction Cost Ratio (TCR)
    - The ratio of the size of the transaction vs the costs involved.

Automatic Transaction Cost Threshold (ATCS)
    - The limit of TCR, below which an automatic transaction will not be performed.
'''

'''
Overnight Process
- Download New Data
- Clear redis instruments cache and recalculate for the day, setting a 4 day timeout to cover weekends/holidays.
- Calculate the new markowitz lambda bounds.
- Process any position adjustments from market fills
    - update the Position model and the Execution/ExecutionDistribution/Transaction models accordingly
- Process any external transfers that were executed in or out from each account.
- Write the days balance for each goal to the HistoricalBalance model. Calculate from yesterday's figure.
- Measure all metrics on goals
  - This calculates drift
- For every account, build a map of goal.id -> experimental_settings, which will be populated for each goal that has a
  change.
  - Process any market changes needed because of the new asset weights.
  - Process Pending Deposits/withdrawals.
    - Any pending deposit gets transferred from the account.cash_balance to the goal_cash_balance.
    - All Netted transactions get moved to 'executed'.
    - Any net withdrawal gets created as a new withdrawal if it doesn't match exactly a current pending withdrawal.
  - Build a list of Execution Requests for each goal based on a rebalance and tax loss harvest for each goal.
  - Confirming any execution requests:
    - Build a market order.
    - Determine cost of order
    - If ATCS is not met, don't send to market. Notify User/Advisor somehow.
    - Depending if the customer is fully managed or not, we may need to put the new market positions into a 'pending'
      state and confirm the rebalance. Confirming rebalances should be a selectable feature per account either way.
      - If position adjustments and existing 'pending' market position change, drop existing pending change.

 - Once the nightly process is done, compare the markowitz cost of the resulting portfolio against the daily optimum
   for this goal. This is the optimisation_drift. If it's over some percent different,
   inform the Client and Advisor that the portfolio needs to be reoptimised.
 - Inform client and advisor if a goal has expired.


'''

'''
  Advisor/ Client Rebalance confirmation
    - We need to indicate to the Client/Advisor:
      - which rebalances need extra cash,
      - which ones went through (and what was the cost)
      -

'''


'''
Once a week, on the weekend, check the last HistoricalBalance record matched a full build from all history, and any
reconciled amount from the broker
'''