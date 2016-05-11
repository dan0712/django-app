import datetime
import operator

from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from pinax.eventlog.models import Log

from rest_framework import serializers
from rest_framework.response import Response

from api.v1.serializers import QueryParamSerializer
from common.constants import EPOCH_TM
from main.event import Event
from main.models import ActivityLog, ActivityLogEvent, Transaction, Goal, ClientAccount, HistoricalBalance


# Map of transaction reason to event
TX2E = {
    Transaction.REASON_DEPOSIT: Event.GOAL_DEPOSIT_EXECUTED,
    Transaction.REASON_EXECUTION: Event.GOAL_ORDER_DISTRIBUTION,
    Transaction.REASON_WITHDRAWAL: Event.GOAL_WITHDRAWAL_EXECUTED,
    Transaction.REASON_DIVIDEND: Event.GOAL_DIVIDEND_DISTRIBUTION,
    Transaction.REASON_FEE: Event.GOAL_FEE_LEVIED,
    Transaction.REASON_REBALANCE: Event.GOAL_REBALANCE_EXECUTED,
    Transaction.REASON_TRANSFER: Event.GOAL_TRANSFER_EXECUTED,
}

class ActivityQueryParamSerializer(QueryParamSerializer):
    sd = serializers.DateField(required=False)
    ed = serializers.DateField(required=False)


def get_transactions(sd, ed, goal_ids):
    qs = (
        Transaction.objects.all()
        .filter(Q(to_goal__in=goal_ids) | Q(from_goal__in=goal_ids))
        .exclude(executed=None)
    )

    if sd is not None:
        qs = qs.filter(executed__gte=sd)
    if ed is not None:
        qs = qs.filter(executed__lte=ed)

    return {tx.id: tx for tx in qs}


def parse_event_logs(logs, transactions, goal):
    # Get the map from event 'action' code to ActivityLog id
    eid2aid = dict(ActivityLog.objects.all().values_list('events__id', 'id'))
    aid2args = dict(ActivityLog.objects.all().values_list('id', 'format_args'))

    items = []
    for log in logs:
        e = Event[log.action]
        # All log items have a type and time. If there is no ActivityLog type registered for the event, it means
        # the operator may not have wanted it included, so skip it.
        tp = eid2aid.get(e.value, None)
        if tp is None:
            continue

        tm = int((timezone.make_naive(log.timestamp) - EPOCH_TM).total_seconds())
        result = {
            'type': tp,
            'time': tm
        }

        # If we're looking at a goal transaction log, add the transaction to the available fields
        if e in Transaction.EXECUTION_EVENTS:
            txid = log.extra.get('txid', None)
            if txid is None:
                raise Exception("Transaction event log: {} has no txid.".format(log.id))
            tx = transactions.pop(txid, None)
            if tx is None:
                raise Exception("Transaction matching event log: {} does not exist.".format(log.id))

            # Only show goal-goal transfers once per account.
            if goal is None and tx.to_goal is not None and tx.from_goal is not None and tx.from_goal.id == max(tx.from_goal.id, tx.to_goal.id):
                continue
            log.extra['transaction'] = model_to_dict(tx)
            if goal is not None:
                result['amount'] = tx.amount if tx.to_goal is not None and tx.to_goal.id == goal.id else -tx.amount

        # Get extra data if necessary
        args = aid2args.get(tp, None)
        if args:
            data = []
            for locstr in map(str.strip, args.strip().splitlines()):
                item = log.extra
                for branch in locstr.split('.'):
                    item = item[branch]
                data.append(item)
            result['data'] = data

        # Get Goal if necessary
        if goal is None and isinstance(log.obj, Goal):
            result['goal'] = log.object_id
        items.append(result)

    # Process any remaining transactions that have no log.
    if goal is not None:
        for tx in transactions.values():
            aid = eid2aid.get(TX2E[tx.reason].value, None)
            # if there is no aid, the transaction probably is still there as it wasn't processed as part of the event logs.
            if aid is None:
                continue

            result = {
                'type': aid,
                'time': int((timezone.make_naive(tx.executed) - EPOCH_TM).total_seconds()),
                'amount': tx.amount if tx.to_goal is not None and tx.to_goal.id == goal.id else -tx.amount
            }
            args = aid2args.get(aid, None)
            if args:
                tx_as_dict = {'transaction': model_to_dict(tx)}
                data = []
                for locstr in map(str.strip, args.strip().splitlines()):
                    item = tx_as_dict
                    for branch in locstr.split('.'):
                        if item != 'UNKNOWN':
                            item = item.get(branch, 'UNKNOWN')
                    data.append(item)
                result['data'] = data
            items.append(result)

    return items


def get(request, obj):
    if isinstance(obj, Goal):
        goal = obj
        goal_ids = [goal.id]
        # Filter for only the events where the object is account or goal
        ctm = ContentType.objects.get_for_models(ClientAccount, Goal)
        el_filter = (Q(content_type=ctm[ClientAccount], object_id=obj.id) |
                     Q(content_type=ctm[Goal], object_id__in=goal_ids))
    elif isinstance(obj, ClientAccount):
        goal = None
        goal_ids = obj.goals.values_list('id', flat=True)
        gct = ContentType.objects.get_for_model(Goal)
        el_filter = (Q(content_type=gct, object_id__in=goal_ids))
    else:
        raise Exception("object type: {} not supported.".format(type(obj)))

    query_params = ActivityQueryParamSerializer.parse(request.query_params)
    sd = query_params.get('sd', None)
    ed = query_params.get('ed', None)

    # Get the eventlog activity items
    date_constraint = Q()
    if sd is not None:
        date_constraint &= Q(date__gte=sd)
    if ed is not None:
        date_constraint &= Q(date__lte=ed)
    events = Log.objects.filter(el_filter & date_constraint)

    # Get all the transactions for the period
    transactions = get_transactions(sd, ed, goal_ids)
    items = parse_event_logs(events, transactions, goal)

    # Get the balances
    tp = ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id
    qs = HistoricalBalance.objects.filter(date_constraint, goal__in=goal_ids).values('date').annotate(sum=Sum('balance'))

    # Join the two lists to one sorted on date
    items.extend([{'type': tp,
                   'time': int((datetime.datetime.combine(bal['date'], datetime.time()) - EPOCH_TM).total_seconds()),
                   'balance': bal['sum']} for bal in qs])
    return Response(sorted(items, key=operator.itemgetter("time")))
