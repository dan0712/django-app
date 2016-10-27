from __future__ import unicode_literals

import datetime

from common.constants import EPOCH_DT


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


def dt2ed(dt: datetime.datetime) -> int:
    """
    Converts a datetime to number of complete days since epoch
    :param dt: The datetime to convert
    :return: An integer of the number of full days since epoch.
    """
    return (dt.date() - EPOCH_DT).days


def d2ed(d: datetime.date) -> int:
    """
    Converts a date to number of complete days since epoch
    :param d: The date to convert
    :return: An integer of the number of full days since epoch.
    """
    return (d - EPOCH_DT).days
