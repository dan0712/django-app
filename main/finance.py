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
        try:
            days = (tr.created.date() - start_date).days
        except TypeError:
            days = 0
            start_date = tr.created.date()
        cash_flows.append((
            days,
            -tr.amount if tr.from_goal is not None else tr.amount
        ))
    cash_flow_balance = sum(i[1] for i in cash_flows)
    total_days = (now().date() - start_date).days
    prorated_sum = sum(cfi * (total_days - d) / total_days
                       for d, cfi in cash_flows)
    return (end_value - begin_value -
            cash_flow_balance) / (begin_value + prorated_sum)
