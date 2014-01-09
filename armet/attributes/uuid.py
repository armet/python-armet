# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .attribute import Attribute
from armet import exceptions
import uuid


try:
    import shortuuid

except ImportError:
    shortuuid = None


class UUIDAttribute(Attribute):

    type = uuid.UUID

    def __init__(self, *args, **kwargs):
        super(UUIDAttribute, self).__init__(*args, **kwargs)

        #! Encode and decode the UUID using 'shortuuid' (only if available).
        self.short = kwargs.get('short')
        if self.short is None or self.short:
            if shortuuid is None:
                if self.short is None:
                    self.short = False
                    return

                else:
                    raise exceptions.ImproperlyConfigured(
                        "Use of 'short' UUID attributes requires the "
                        "'shortuuid' package.")

            # Default to using short UUIDs if we have the package.
            self.short = True

    def prepare(self, value):
        if value is None:
            return None

        if self.short:
            # Serialize as a 22-digit hex representation.
            return shortuuid.encode(value)

        # Serialize as the 32-digit hex representation.
        return value.hex

    def clean(self, value):
        if value is None:
            # Value is nothing; return it.
            return value

        try:
            try:
                if self.short:
                    # Attempt to coerce the short UUID.
                    return shortuuid.decode(value)

            except ValueError:
                pass

            # Attempt to coerce the UUID.
            return uuid.UUID(value)

        except ValueError:
            raise ValueError(
                'UUID must be of the form: '
                'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
