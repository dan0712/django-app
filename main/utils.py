from __future__ import unicode_literals

import datetime


def d2dt(d: datetime.date) -> datetime.datetime:
    if isinstance(d, datetime.date):
        d = datetime.datetime(year=d.year, month=d.month, day=d.day, tzinfo=None)
    return d


def dt2d(dt: datetime.datetime) -> datetime.date:
    if isinstance(dt, datetime.datetime):
        dt = dt.date()
    return dt
