import datetime

import decimal

# Make unsafe float operations with decimal fail
decimal.getcontext().traps[decimal.FloatOperation] = True

EPOCH_TM = datetime.datetime.utcfromtimestamp(0)
EPOCH_DT = EPOCH_TM.date()
DEC_2PL = decimal.Decimal('1.00')