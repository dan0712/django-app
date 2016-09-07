from __future__ import unicode_literals
import datetime
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from main.models import RecurringTransaction
from main.tests.fixture import Fixture1


mocked_now = mock.Mock(return_value=datetime.datetime(2016, 8, 12, 13, 0, 0,
                                                      tzinfo=timezone.utc))


class TransferPlanAbstractTest(TestCase):
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

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_transfer_amount(self):
        print(timezone.now())
        ta = self.rt.transfer_amount(timezone.now() + datetime.timedelta(days=10))
        self.assertEqual(ta, 10.050112650131325)

    @mock.patch.object(timezone, 'now', mocked_now)
    def test_next(self):
        date = timezone.now() + datetime.timedelta(days=10)
        d, v = self.rt.get_next(date)
        self.assertEqual((d.date(), v), (datetime.date(2016, 9, 4), 10.115634719294892))

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
        dd = [
            datetime.date(2016, 9, 4),
            datetime.date(2016, 10, 4),
            datetime.date(2016, 11, 4)
        ]
        for i, (d, v) in enumerate(between):
            self.assertEqual((d.date(), v), (dd[i], vv[i]))
