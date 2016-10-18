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
    for tr in transactions:
        amount = -tr.amount if tr.from_goal is not None else tr.amount
        try:
            cash_flows.append((
                (tr.created.date() - start_date).days,
                amount,
                tr.created.date()
            ))
        except TypeError:  # start_date is None
            # use date of the first transaction as opening date
            # and it's not a part of cashflow
            start_date = tr.created.date()
            begin_value = amount

    if not transactions:
        return 0

    if not end_value and cash_flows:  # all goals have zero balance
        # get closing date and balance from the last transaction
        _, end_value, closing_date = cash_flows.pop()
        # last transaction is withdrawal with negative amount,
        # and balance must be positive
        end_value = abs(end_value)
    else:
        closing_date = now().date()

    cash_flow_balance = sum(i[1] for i in cash_flows)
    total_days = (closing_date - start_date).days

    # Since we can have a goal with start=end=today()
    # It makes sense to show the return as if total_days=1
    if total_days == 0:
        total_days = 1
    prorated_sum = sum(cfi * (total_days - d) / total_days
                       for d, cfi, _ in cash_flows)
    result = (end_value - begin_value -
              cash_flow_balance) / (begin_value + prorated_sum)
    annualised_return = pow(1 + result, 365.25 / total_days) - 1
    return annualised_return
