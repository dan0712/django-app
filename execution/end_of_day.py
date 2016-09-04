import logging
from django.db import transaction
from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from time import sleep, strftime, time
from client.models import ClientAccount
from execution.broker.interactive_brokers import InteractiveBrokers

short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)

verbose_levels = {
    3 : DEBUG,
    2 : INFO,
    1 : WARN,
    0 : ERROR,
    }

ib_account_list = list()
ib_account_cash = dict()

logger = logging.getLogger('betasmartz.daily_process')
logger.setLevel(logging.INFO)


class Object(object):
    pass


def get_options():
    opts = Object()
    opts.verbose = 0
    return opts


def reconcile_cash_client_account(account):
    with transaction.atomic():
        account_cash = account.cash_balance
        goals = account.goals.all()

        goals_cash = 0
        for goal in goals:
            goals_cash += goal.cash_balance

        ib_account = account.ib_account.get(bs_account_id=account.id)
        ib_cash = ib_account_cash[ib_account.ib_account]

        difference = ib_cash - (account_cash + goals_cash)
        if difference > 0:
            #there was deposit
            account_cash += difference
        elif difference < 0:
            #withdrawals
            if abs(difference) < account_cash:
                account_cash -= abs(difference)
            else:
                logger.exception("interactive brokers cash < sum of goals cashes for " + account.account_id)
                raise Exception
                # we have a problem - we should not be able to withdraw more than account_cash
        account.cash_balance = account_cash
        account.save()
        return difference


def reconcile_cash_client_accounts():
    client_accounts = ClientAccount.objects.all()
    with transaction.atomic():
        for account in client_accounts:
            try:
                reconcile_cash_client_account(account)
            except:
                print("exception")


def main(options):
    logging.root.setLevel(verbose_levels.get(options.verbose, ERROR))
    con = InteractiveBrokers()
    con.connect()
    short_sleep()
    con.request_account_summary()
    long_sleep()
    ib_account_cash.update(con.ib_account_cash)
    reconcile_cash_client_accounts()


if __name__ == '__main__':
    try:
        main(get_options())
    except:
        print("exception")