from client.models import ClientAccount, IBAccount
from main.models import MarketOrderRequest, ExecutionRequest, Execution, Ticker


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
            allocation_per_ib_account = allocation_per_ib_id[ib_account]
            Execution.objects.create(asset=Ticker.objects.get(symbol=order_fills[ib_id].symbol),
                                     volume=allocation_per_ib_account.shares,
                                     order=mor,
                                     price=allocation_per_ib_account.price,
                                     amount=allocation_per_ib_account.shares * allocation_per_ib_account.price,
                                     executed=allocation_per_ib_account.time[-1])
        #TODO get amount from IB - including transaction costs
        #TODO distributions - alphabetical order - maybe good enough