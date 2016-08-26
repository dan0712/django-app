from __future__ import unicode_literals

from typing import Iterable

from django.db.models import Q
from django.utils.timezone import now


def mod_dietz_rate(goals: Iterable) -> float:
    from main.models import Transaction

    end_value = sum(g.total_balance for g in goals)
    begin_value = 0
    cash_flows = []
    start_date = None
    transactions = (
        Transaction.objects.filter(
            Q(from_goal__in=goals) | Q(to_goal__in=goals),
            Q(reason=Transaction.REASON_WITHDRAWAL) |
            Q(reason=Transaction.REASON_DEPOSIT),
            status=Transaction.STATUS_EXECUTED
        ).order_by('created'))
    if not transactions:
        return 0
    for tr in transactions:
        amount = -tr.amount if tr.from_goal is not None else tr.amount
        try:
            cash_flows.append((
                (tr.created.date() - start_date).days,
                amount
            ))
        except TypeError:  # start_date is None
            # use date of the first transaction as opening date
            start_date = tr.created.date()
            begin_value = amount

    cash_flow_balance = sum(i[1] for i in cash_flows)
    # find all goals with zero balance
    zero_balanced = [g for g in goals if not g.total_balance]
    if zero_balanced:
        # get their last transactions
        last_transaction_dates = []
        transaction_list = list(reversed(list(transactions)))
        for g in zero_balanced:
            for tr in transaction_list:
                if tr.from_goal == g or tr.to_goal == g:
                    last_transaction_dates.append(tr.created.date())
                    break
        closing_date = min(last_transaction_dates)
        # TODO what if some goal got zero balance and some time after
        # TODO another goal had a transaction
    else:
        closing_date = now().date()
    total_days = (closing_date - start_date).days
    prorated_sum = sum(cfi * (total_days - d) / total_days
                       for d, cfi in cash_flows)
    result = (end_value - begin_value -
              cash_flow_balance) / (begin_value + prorated_sum)
    annualised_return = pow(1 + result, 365.25/total_days) - 1
    return annualised_return
