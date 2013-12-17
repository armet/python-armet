# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import exceptions
from .attribute import Attribute


try:
    # TODO: List this somewhere as an optional dep.
    import pytz

except ImportError:
    # No timezone support.
    pytz = None


class TimezoneAttribute(Attribute):

    if pytz is not None:
        type = pytz.tzfile.DstTzInfo

    def __init__(self, *args, **kwargs):
        # Ensure we have support.
        if pytz is None:
            raise exceptions.ImproperlyConfigured(
                'Use of the timezone attribute requires pytz')

        # Continue on.
        super(TimezoneAttribute, self).__init__(*args, **kwargs)

    def prepare(self, value):
        return value.zone

    def clean(self, value):
        if value is None:
            # Value is nothing; return it.
            return value

        try:
            # Attempt to coerce the timezone.
            return pytz.timezone(value)

        except pytz.UnknownTimeZoneError:
            raise ValueError('Unknown time zone.')
