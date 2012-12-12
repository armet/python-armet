# -*- coding: utf-8 -*-
"""Defines proxies to primitive types to fluff their properties.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import datetime
import decimal
import fractions
import six
import collections


class NullProxy(object):
    """A null proxy that denies access to object properties.
    """

class ComplexProxy(object):

    @property
    def real(obj):
        """The real part of this complex number."""
        return obj.real

    @property
    def imag(obj):
        """The imaginary part of this complex number."""
        return obj.imag


class StringProxy(collections.Sequence):

    def __contains__(obj, key):
        return key in obj

    def __iter__(obj):
        return iter(obj)

    def __getitem__(obj, index):
        return obj[index]

    @property
    def length(obj):
        """The number of characters in this string."""
        return len(obj)


class TemporalProxy(object):

    @property
    def ordinal(obj):
        """The proleptic Gregorian ordinal of this date/time."""
        return obj.toordinal()


class DateProxy(TemporalProxy):

    @property
    def year(obj):
        """The 4-digit year."""
        return obj.year

    @property
    def month(obj):
        """The month from 1 to 12."""
        return obj.month

    @property
    def day(obj):
        """The day of the month from 1 to the number of days in the month."""
        return obj.day

    @property
    def weekday(obj):
        """The day of the week where Monday is 1 and Sunday is 7 (ISO)."""
        return obj.isoweekday()

    @property
    def yearday(obj):
        """The day of the year from 1 to 366."""
        return obj.timetuple().tm_yday


class TimeProxy(TemporalProxy):

    @property
    def hour(obj):
        """The hour of this date/time."""
        return obj.hour

    @property
    def minute(obj):
        """The minute of this date/time."""
        return obj.minute

    @property
    def second(obj):
        """The second of this date/time."""
        return obj.second

    @property
    def millisecond(obj):
        """The fractional part of the second of this date/time, in ms."""
        return obj.microsecond / 1000.0

    @property
    def microsecond(obj):
        """The fractional part of the second of this date/time, in us."""
        return obj.microsecond

    @property
    def dst(obj):
        """The applied offset for daylight savings time, if in effect."""
        value = obj.dst()
        return value if value is not None else datetime.timedelta()

    @property
    def timezone(obj):
        """The name of the timezone in which this date/time is defined."""
        return obj.tzname()

    @property
    def offset(obj):
        """The offset from UTC for the timezone this date/time is defined."""
        value = obj.utcoffset()
        return value if value is not None else datetime.timedelta()


class DateTimeProxy(DateProxy, TimeProxy):
    pass


def find(cls):
    """Attempt to determine what kind of proxy to use."""
    try:
        if issubclass(cls, complex):
            # A complex number
            return ComplexProxy

    except NameError:
        # No complex support
        pass

    if (issubclass(cls, six.integer_types)
            or issubclass(cls, float)
            or issubclass(cls, decimal.Decimal)
            or issubclass(cls, fractions.Fraction)):
        # Some kind of something
        return NullProxy

    if issubclass(cls, datetime.datetime):
        # A date/time instance
        return DateTimeProxy

    if issubclass(cls, datetime.date):
        # A date instance
        return DateProxy

    if issubclass(cls, datetime.time):
        # A time instance
        return TimeProxy

    if issubclass(cls, six.string_types):
        # A string
        return StringProxy

    # No proxy needed; return nothing
