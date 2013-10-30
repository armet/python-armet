# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .attribute import Attribute
import datetime
from armet import exceptions


try:
    # Attempt to import and make use of date/time libraries.
    # TODO: Make note of this optional dep somewhere.
    from dateutil.parser import parse as parse_datetime
    from time import mktime

except ImportError:
    # No support for date/times.
    parse_datetime = None


class _TemporalAttribute(Attribute):
    """Represents a temporal attribute, such as a date or time.
    """

    def __init__(self, *args, **kwargs):
        # Ensure we have support.
        if parse_datetime is None:
            raise exceptions.ImproperlyConfigured(
                'Use of temporal attributes requires at '
                'least python-dateutil (and optionally parsedatetime).')

        # Continue on.
        super(_TemporalAttribute, self).__init__(*args, **kwargs)

    def prepare(self, value):
        if not value:
            return None

        # Serialize as ISO format.
        return value.isoformat()

    def clean(self, value):
        if not value:
            # Value is nothing; return it.
            return value

        try:
            # Attempt to use the dateutil library to parse.
            return parse_datetime(value, fuzzy=False)

        except (ValueError, AttributeError):
            # Not a strictly formatted date; return nothing.
            pass

        try:
            # Attempt to magic a date out of it.
            # TODO: List this somewhere as an optional dep.
            from parsedatetime import parsedatetime as pdt
            c = pdt.Constants()
            c.BirthdayEpoch = 80  # TODO: Figure out what this is.
            p = pdt.Calendar(c)
            result = p.parse(value)
            if result[1] != 0:
                return datetime.datetime.fromtimestamp(mktime(result[0]))

        except (NameError, ImportError, TypeError):
            # No magical date/time support.
            pass

        # Couldn't figure out what we're dealing with.
        raise ValueError('Invalid date/time or in an invalid format.')


class DateAttribute(_TemporalAttribute, Attribute):

    type = datetime.date

    def clean(self, value):
        value = super(DateAttribute, self).clean(value)
        if value:
            # Constrain to just the date part.
            value = value.date()
        return value


class TimeAttribute(_TemporalAttribute, Attribute):

    type = datetime.time

    def clean(self, value):
        value = super(TimeAttribute, self).clean(value)
        if value:
            # Constrain to just the date part.
            value = value.time()
        return value


class DateTimeAttribute(_TemporalAttribute, Attribute):

    type = datetime.datetime
