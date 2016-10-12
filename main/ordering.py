from django.db import transaction

from main.models import MarketOrderRequest, Transaction, ExecutionRequest, Ticker
from main.event import Event


class OrderingError(Exception):
    pass


class OrderManager(object):
    """
    The Order manager is the interface between the external ordering system and our internal django application code.
    All actions to any order (except initial creation) should be performed through this class. It ensure all appropriate
    record-keeping is done, and all states etc are transitioned correctly.
    """

    @staticmethod
    def place_order(request, reason):
        """
        Sends an order to the market.
        :param request:
            A MarketOrderRequest or similar that describes the order to be sent to market.
            The request must be in the 'approved' state, or an OrderingError will be raised.
        :param reason: The reason for the order.
        :return: integer async_request_id. None if the action was executed synchronously
        """
        if request.state != MarketOrderRequest.State.APPROVED:
            emsg = "Cannot place order request {} that is not in the 'approved' state."
            raise OrderingError(emsg.format(request))

        Event.PLACE_MARKET_ORDER.log(reason, request, obj=request)

        # TODO: Here we hook into the external ordering system

        # For the moment, we're doing nothing, so tell the caller it has completed synchronously
        return None

    @staticmethod
    def cancel_order(request, reason):
        """
        Cancel an outstanding order request.
        :param request: The order request to cancel. If the request is not in an open state, this is a noop
        :param reason: The reason for the order cancel.
        :return: integer async_request_id. None if the action was executed synchronously
        """
        if request.state not in MarketOrderRequest.OPEN_STATES:
            # Nothing to do, so tell the caller it has completed synchronously
            return None

        Event.CANCEL_MARKET_ORDER.log(reason, request.id, obj=request)

        # TODO: Send the cancel to market

        # For the moment, we're doing nothing, so tell the caller it has completed synchronously
        return None

    @staticmethod
    def cancel_replace(old_request, new_request, reason):
        """
        Cancel an outstanding order request and replace it with a new one.
        :param old_request:
            The old request you want to replace. If the request is not in an open state, an OrderingError is raised
        :param new_request:
            The new request you want to replace the old with. If the request is not approved, an OrderingError is raised
        :param reason: The reason for the order replace.
        :return: integer async_request_id. None if the action was executed synchronously
        """
        if old_request.state not in MarketOrderRequest.OPEN_STATES:
            raise OrderingError("Existing order request: {} is not in an open state.".format(old_request))
        if new_request.state != MarketOrderRequest.State.APPROVED:
            raise OrderingError("Replacement order request: {} is not in an approved state.".format(new_request))

        # TODO: Send the cancel to market

        # TODO: Queue the placement of the new order on successful cancellation of the old.

        # For the moment, we're doing nothing, so tell the caller it has completed synchronously
        return None

    @staticmethod
    @transaction.atomic
    def close_positions(goal):
        """
        Create close position requests for all the positions owned by the given goal.
        :param goal: The goal you want to close the positions of.
        :return: A MarketOrderRequest if the goal had positions.
        """

        # Make sure this goal has no open MarketOrderRequests that include this goal.
        async_id = OrderManager.cancel_open_orders(goal)

        # Send whatever neutralising orders need to be sent
        positions = goal.get_positions_all()
        if async_id is None and positions:
            order_request = MarketOrderRequest.objects.create(account=goal.account)
            execution_requests = []
            transactions = []
            for position in positions:
                # We should never be short.
                if position.quantity < 0:
                    raise ValueError("We have a negative position, and we should NEVER have that.")
                transactions.append(Transaction(reason=Transaction.REASON_ORDER,
                                                to_goal=goal,
                                                amount=position.price * position.quantity))
                execution_requests.append(ExecutionRequest(reason=ExecutionRequest.Reason.WITHDRAWAL,
                                                           goal=goal,
                                                           asset=Ticker.objects.get(position.ticker_id),
                                                           volume=-position.quantity,
                                                           order=order_request,
                                                           transaction=transactions[-1]))
            Transaction.objects.bulk_create(transactions)
            ExecutionRequest.objects.bulk_create(execution_requests)
            return order_request
        else:
            # First stage was asynchronous, we need to wait
            # TODO: Queue up another call to close_positions based on the completion of async_id
            raise NotImplementedError("Need to implement async logic.")

    @staticmethod
    def get_open_orders(goal):
        reqs = MarketOrderRequest.objects.filter(account=goal.account, state__in=MarketOrderRequest.OPEN_STATES)
        res = []
        for req in reqs:
            for ereq in req.execution_requests.all():
                if ereq.goal == goal:
                    res.append(req)
                    break
        return res

    @staticmethod
    @transaction.atomic
    def cancel_open_orders(goal):
        """
        Cancel all open order requests for a goal
        :param goal:
        :return: integer async_request_id. None if the action was completed synchronously
        """
        for order in OrderManager.get_open_orders(goal):
            # Create a new order request based on the old one, but removing any execution requests for this goal
            nreqs = order.execution_requests.exclude(goal=goal)
            if len(nreqs) > 0:
                norder = MarketOrderRequest.objects.create(account=order.account)
                for req in nreqs:
                    tx = Transaction.objects.create(
                        reason=req.transaction.reason,
                        from_goal=req.transaction.from_goal,
                        to_goal=req.transaction.to_goal,
                        amount=req.transaction.amount,
                    )
                    # Create the new execution requeests for what was left over off the old request now the goal is gone
                    ExecutionRequest.objects.create(
                        reason=req.reason,
                        goal=req.goal,
                        asset=req.asset,
                        volume=req.volume,
                        order=norder,
                        transaction=tx,
                    )
                reason = 'Closing positions for goal: {} that was on a shared MarketOrderRequest'.format(goal)
                return OrderManager.cancel_replace(order, norder, reason)
            else:
                reason = 'Closing positions for goal: {}'.format(goal)
                return OrderManager.cancel_order(order, reason)
