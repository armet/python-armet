# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .attribute import Attribute
import uuid


class UUIDAttribute(Attribute):

    type = uuid.UUID

    def prepare(self, value):
        # Serialize as the 16-digit hex representation.
        return value.hex if value else value

    def clean(self, value):
        if value is None:
            # Value is nothing; return it.
            return value

        try:
            # Attempt to coerce the UUID.
            return uuid.UUID(value)

        except ValueError:
            raise ValueError(
                'UUID must be of the form: '
                'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
