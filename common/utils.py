from __future__ import unicode_literals

import datetime


def months_between(date1, date2):
    if date1 > date2:
        date1, date2 = date2, date1
    m1 = date1.year*12 + date1.month
    m2 = date2.year*12 + date2.month
    return m2 - m1


def d2dt(d: datetime.date) -> datetime.datetime:
    if isinstance(d, datetime.date):
        d = datetime.datetime(year=d.year, month=d.month, day=d.day, tzinfo=None)
    return d


def dt2d(dt: datetime.datetime) -> datetime.date:
    if isinstance(dt, datetime.datetime):
        dt = dt.date()
    return dt
