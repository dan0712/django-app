from client.models import ClientAccount, IBAccount
from main.models import MarketOrderRequest, ExecutionRequest, Execution, Ticker, Transaction, \
    ExecutionDistribution



def create_django_executions(order_fills, execution_allocations):
    '''
    :param order_fills: Order
    :param execution_allocations: AccountAllocations
    :return:
    '''
    for ib_id in execution_allocations.keys():
        allocation_per_ib_id = execution_allocations[ib_id]

        for ib_account in allocation_per_ib_id.keys():
            account = IBAccount.objects.get(ib_account=ib_account)
            client_account = ClientAccount.objects.get(ib_account=account)

            mor = MarketOrderRequest.objects.get(account=client_account, state=MarketOrderRequest.State.APPROVED.value)

            ers = ExecutionRequest.objects.all().filter(order__account__ib_account__ib_account=ib_account)
            allocation_per_ib_account = allocation_per_ib_id[ib_account]
            no_shares = allocation_per_ib_account.shares
            for e in ers:
                to_subtract = min(no_shares, e.volume)
                no_shares -= to_subtract
                ex1 = Execution.objects.create(asset=Ticker.objects.get(symbol=order_fills[ib_id].symbol),
                                               volume=to_subtract,
                                               order=mor,
                                               price=allocation_per_ib_account.price,
                                               amount=to_subtract * allocation_per_ib_account.price,
                                               executed=allocation_per_ib_account.time[-1])

                t1 = Transaction.objects.create(reason=Transaction.REASON_EXECUTION,
                                                to_goal=None,
                                                from_goal=e.goal,
                                                status=Transaction.STATUS_EXECUTED,
                                                executed=allocation_per_ib_account.time[-1],
                                                amount=to_subtract * allocation_per_ib_account.price)\

                ExecutionDistribution(execution=ex1, transaction=t1, volume=to_subtract)
                e.delete()

        #TODO get amount from IB - including transaction costs
