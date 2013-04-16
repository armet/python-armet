# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import collections
import six


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
        #!
        #! The path may be dot-separated to indicate simple traversal.
        #! Eg. user.name could be obj['user'].name
        self.path = path

        if self.path:
            # Explode the path into segments.
            self._segments = path.split('.')

            # Initialize the accessors array.
            self._accessors = []

    def _make_accessor(self, path, cls, value):
        # Attempt to get an unbound class property
        # that may be a descriptor.
        obj = getattr(cls, path, None)
        if obj is not None:
            if hasattr(obj, '__call__'):
                # The descriptor is callable.
                return lambda o, x=obj.__call__: x(o)

        else:
            # Check for another kind of descriptor.
            descriptor = cls.__dict__.get(path)
            if descriptor and hasattr(descriptor, '__get__'):
                return lambda o, x=descriptor.__get__: x(o)

        if issubclass(cls, collections.Mapping):
            return lambda o, n=path: o.get(n)

        if issubclass(cls, collections.Sequence):
            path = int(path)
            if path == 0:
                # Sequence access is 1-indexed.
                def accessor(obj):
                    raise TypeError()

            else:
                path = path - 1 if path > 0 else path

                def accessor(obj, index=path):
                    if isinstance(obj, six.string_types) and len(obj) == 1:
                        # We cannot index into a 'character'.
                        raise TypeError()

                    # Return the element.
                    return obj[index]

            # Return the built accessor.
            return accessor

        # No alternative; let's pretend this will work (which it will
        # most of the time).
        return lambda o, n=path: o.__dict__[n]

    def get(self, value):
        """Retrieves the value of this attribute from the passed object."""
        if not self.path:
            # If we do not have a path; we cannot automatically
            # resolve our value; return nothing.
            return None

        for accessor in self._accessors:
            # Iterate and resolve the attribute path.
            value = accessor(value)

        if value is not None and self._segments:
            # Value isn't none and we still have additional segments left
            # to resolve into accessors.
            for index, segment in enumerate(self._segments):
                if value is None:
                    # We no longer have a value to use to attempt
                    # to resolve additional segments; bail for now.
                    break

                # Build the accessor corresponding to this path
                # segment.
                accessor = self._make_accessor(
                    segment, value.__class__, value)

                # Append the accessor.
                self._accessors.append(accessor)

                # Utilize the accessor now.
                value = accessor(value)

            # Remove any path segments that have been resolved
            # into accessors.
            del self._segments[:index + 1]

        # Return what has been accessed.
        return value

    def prepare(self, value):
        """Prepares the value for serialization."""
        return str(value)

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


class IntegerAttribute(Attribute):
    """Represents an integer; serialzied as a python integer.
    """

    def clean(self, value):
        if isinstance(value, six.string_types):
            # Strip the string of whitespace
            value = value.strip()

        try:
            # Attempt to coerce whatever we have as an int.
            return int(value)

        except ValueError:
            # Failed to do so.
            return None
