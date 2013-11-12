# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .attribute import Attribute


class BooleanAttribute(Attribute):

    type = bool

    #! Textual values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on',
        '1'
    )

    #! Textual values accepted for `False`.
    FALSE = (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    )

    def clean(self, value):
        if value is None:
            # Value is nothing; return it.
            return value

        if value is True or value is False:
            # Value is a python boolean; just return it.
            return value

        if value.strip().lower() in self.TRUE:
            # Some sort of truthy value.
            return True

        if value.strip().lower() in self.FALSE:
            # Some sort of falsy value.
            return False

        # Neither true or false matches; return a boolifyed version of
        # whatever we have.
        return bool(value)


class TextAttribute(Attribute):

    type = six.text_type

    def clean(self, value):
        return six.text_type(value) if value is not None else None


class IntegerAttribute(Attribute):

    type = int

    def clean(self, value):
        if isinstance(value, six.integer_types):
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
            return int(value)

        except ValueError:
            # Failed to do so.
            raise ValueError('Not a valid integral value.')
