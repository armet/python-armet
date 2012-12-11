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


class NumericProxy(object):

    @property
    def numerator(obj):
        return obj.numerator

    @property
    def denominator(obj):
        return obj.denominator


class ComplexProxy(object):

    @property
    def real(obj):
        return obj.real

    @property
    def imag(obj):
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
        return len(obj)


class TemporalProxy(object):

    @property
    def ordinal(obj):
        return obj.toordinal()


class DateProxy(TemporalProxy):

    @property
    def year(obj):
        return obj.month

    @property
    def month(obj):
        return obj.month

    @property
    def day(obj):
        return obj.day

    @property
    def weekday(obj):
        return obj.isoweekday()

    @property
    def yearday(obj):
        return obj.timetuple().tm_yday


class TimeProxy(TemporalProxy):

    @property
    def hour(obj):
        return obj.hour

    @property
    def minute(obj):
        return obj.minute

    @property
    def second(obj):
        return obj.second

    @property
    def millisecond(obj):
        return obj.microsecond / 1000.0

    @property
    def microsecond(obj):
        return obj.microsecond

    @property
    def dst(obj):
        value = obj.dst()
        return value if value is not None else datetime.timedelta()

    @property
    def timezone(obj):
        return obj.tzname()

    @property
    def offset(obj):
        return obj.utcoffset()


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
        # Some kind of number
        return NumericProxy

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
