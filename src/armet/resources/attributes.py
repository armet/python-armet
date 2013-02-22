# -*- coding: utf-8 -*-
"""Defines attributes available on a resource object.s
"""
from __future__ import print_function, unicode_literals, division


class Attribute(object):
    """Generic attribute; (de)serialzied as text.
    """

    def __init__(self, path=None, **kwargs):
        """Initializes this attribute with the given properties."""
        #! If this attribute can be read via direct
        #! access (eg. GET /resource/1/attribute)
        #! @warning Not implemented.
        self.readable = kwargs.get('readable', True)

        #! If this attribute can be written via direct
        #! access (eg. PUT /resource/1/attribute) or modification of the
        #! resource (eg. PUT /resource/1 or PATCH /resource/1).
        #! @warning Not implemented.
        self.writable = kwargs.get('writable', True)

        #! If this attribute is included in the resource body.
        #! @warning Not implemented.
        self.include = kwargs.get('include', True)

        #! If this attribute can accept null as a value.
        #! @warning Not implemented.
        self.null = kwargs.get('null', True)

        #! If this attribute must have some value.
        #! @warning Not implemented.
        self.required = kwargs.get('required', True)

        #! If this attribute is represented as a collection (aka. array).
        self.collection = kwargs.get('collection', False)

        #! The path reference of where to find this attribute on an
        #! item (eg. 'name' references the name key if the read method returns
        #! a dictionary.)
        self.path = path

    def prepare(self, value):
        """Prepares the value for serialization."""
        return value

    def clean(self, value):
        """Cleans the value in preparation for deserialization."""
        return value


class BooleanAttribute(Attribute):
    """
    Represents a boolean; serialzied as a python bool and deserialized as
    an actual bool in most decoders.
    """

    #! Textual values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on'
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
