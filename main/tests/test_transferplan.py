from __future__ import unicode_literals

import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from main.models import RecurringTransaction
from main.tests.fixtures import Fixture1


class BaseTest(TestCase):
    def o(self, obj):
        return obj.__class__.objects.get(pk=obj.id)


mocked_now = mock.Mock(return_value=datetime.datetime(2016, 8, 12, 13, 0, 0,
                                                      tzinfo=timezone.utc))


class TransferPlanAbstractTest(BaseTest):
    """
    In most cases time is ignored as the schedule is monthly based,
    and no need to mock the rrule lib that uses datetime.now() that is very
    troublesome to mock
    """

    @mock.patch.object(timezone, 'now', mocked_now)
    def setUp(self):
        self.rt = RecurringTransaction.objects.create(
            setting=Fixture1.settings1(),
            begin_date=timezone.now().date(),
            amount=10,
            growth=0.0005,
            schedule='RRULE:FREQ=MONTHLY;BYMONTHDAY=4'
        )

    def rr_next_date(self, dt, months=1):
        date = dt
        for i in range(months):
            if not i and date.day > 4 or date.day >= 4:
                date += datetime.timedelta(33 - date.day)
            date = date.replace(day=4)
        return date

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_transfer_amount(self):
        print(timezone.now())
        ta = self.rt.transfer_amount(timezone.now().date() +
                                     datetime.timedelta(days=10))
        self.assertEqual(ta, 10.050112650131325)

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_next_date(self):
        date = timezone.now() + datetime.timedelta(days=10)
        next_date = self.rt.get_next_date(date)
        self.assertEqual(next_date.date(), self.rr_next_date(date).date())

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_next(self):
        date = timezone.now() + datetime.timedelta(days=10)
        d,v = self.rt.get_next(date)
        self.assertEqual((d.date(), v),
                         (self.rr_next_date(date).date(), 10.115634719294892))

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_between(self):
        dates = (timezone.now() + datetime.timedelta(days=10),
                 timezone.now() + datetime.timedelta(days=100))
        between = self.rt.get_between(*dates)

        vv = [
            10.115634719294892,
            10.26847446641597,
            10.42883532064945,
        ]
        for i, (d, v) in enumerate(between):
            self.assertEqual((d.date(), v),
                             (self.rr_next_date(dates[0], i+1).date(), vv[i]))
