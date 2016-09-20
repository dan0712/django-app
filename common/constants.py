import datetime

import decimal

from django.utils.translation import gettext_lazy as _

# Make unsafe float operations with decimal fail
decimal.getcontext().traps[decimal.FloatOperation] = True

EPOCH_TM = datetime.datetime.utcfromtimestamp(0)
EPOCH_DT = EPOCH_TM.date()
DEC_2PL = decimal.Decimal('1.00')

KEY_SUPPORT_TICKET = '__support_ticket'

PERM_CAN_CREATE_SUPPORT_REQUESTS = ('can_create_support_requests',
                                    _('Can create support requests'))
GROUP_SUPPORT_STAFF = 'SupportStaff'

WEEKDAYS_PER_YEAR = 260