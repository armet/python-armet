# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .attribute import Attribute
import decimal


class DecimalAttribute(Attribute):

    type = decimal.Decimal

    def prepare(self, value):
        if value is None:
            return None

        return six.text_type(float(value))

    def clean(self, value):
        if isinstance(value, decimal.Decimal):
            # Value is already an integer.
            return value

        if isinstance(value, six.string_types):
            # Strip the string of whitespace
            value = value.strip()

        if not value:
            # Value is nothing; return nothing.
            return None

        try:
            # Attempt to coerce whatever we have as an int.
            return decimal.Decimal(value)

        except (ValueError, decimal.InvalidOperation):
            # Failed to do so.
            raise ValueError('Not a valid decimal value.')
