# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import six
import uuid
import datetime
from armet import exceptions


class Attribute(object):
    """Generic attribute; (de)serialzied as text.
    """

    #! Underyling type of the attribute.
    type = None

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

            # Initialize the getters and setters.
            self._getters = []
            self._setter = None

    def clone(self):
        # Construct a new this.
        return self.__class__(**self.__dict__)

    def _make_getter(self, path, cls, instance):
        # Attempt to get an unbound class property
        # that may be a descriptor.
        obj = getattr(cls, path, None)
        if obj is not None:
            if hasattr(obj, '__call__'):
                # The descriptor is callable.
                return obj.__call__

            if hasattr(obj, '__get__'):
                # This has a data descriptor.
                return lambda o, c=cls, g=obj.__get__: g(o, c)

        else:
            # Check for another kind of descriptor.
            descriptor = cls.__dict__.get(path)
            if descriptor and hasattr(descriptor, '__get__'):
                return descriptor.__get__

        if issubclass(cls, collections.Mapping):
            return lambda o, n=path: o.get(n)

        # No alternative; let's pretend this will work (which it will
        # most of the time).
        return lambda o, n=path: o.__dict__.get(n)

    def _make_setter(self, path, cls, instance):
        # Attempt to get an unbound class property
        # that may be a descriptor.
        obj = getattr(cls, path, None)
        if obj is not None:
            if hasattr(obj, '__set__'):
                # This has a data descriptor.
                return lambda o, v, s=obj.__set__: s(o, v)

        else:
            # Check for another kind of descriptor.
            descriptor = cls.__dict__.get(path)
            if descriptor and hasattr(descriptor, '__set__'):
                return descriptor.__set__

        if issubclass(cls, collections.Mapping):
            def setter(o, v, n=path):
                o[n] = v

            return setter

        # No alternative; let's pretend this will work (which it will
        # most of the time).
        def setter(o, v, n=path):
            o.__dict__[n] = v

        return setter

    def get(self, target, parent=False):
        """Retrieves the value of this attribute from the passed object."""
        if not self.path:
            # If we do not have a path; we cannot automatically
            # resolve our value; return nothing.
            return None

        for getter in self._getters[:-1 if parent else None]:
            # Iterate and resolve the attribute path.
            target = getter(target)

        if self._segments and target is not None:
            # Value isn't none and we still have additional segments left
            # to resolve into getters.
            while self._segments:
                if target is None:
                    # We no longer have a value to use to attempt
                    # to resolve additional segments; bail for now.
                    break

                # Remove any path segments that have been resolved
                # into getters.
                segment = self._segments.pop(0)

                # Build the getter corresponding to this path
                # segment.
                getter = self._make_getter(
                    segment, target.__class__, target)

                # Append the getter.
                self._getters.append(getter)

                if self._segments or not parent:
                    # Utilize the getter now.
                    target = getter(target)

        # Return what has been accessed.
        return target

    def set(self, target, value):
        """Stores the value on the passed target."""
        if not self.path:
            # If we do not have a path; we cannot automatically
            # resolve our value; do nothing.
            return

        # Iterate and resolve the parent of our target.
        parent = self.get(target, parent=True)

        if self._setter is None:
            # Resolve our setter if needed.
            self._setter = self._make_setter(
                self.path.split('.')[-1], parent.__class__, parent)

        # Set the target.
        self._setter(parent, value)

    def prepare(self, value):
        """Prepares the value for serialization."""
        return value

    def clean(self, value):
        """Cleans the value in preparation for deserialization."""
        return value

    def try_clean(self, value):
        """Cleans the value in preparation for deserialization.

        Does not throw errors; returns None if the conversion failed to
        happen.
        """
        try:
            return self.clean(value)

        except ValueError:
            return None


class TextAttribute(Attribute):
    """Represents text.
    """

    type = str

    def prepare(self, value):
        """Stringifies the value."""
        return str(value) if value is not None else None


class BooleanAttribute(Attribute):
    """
    Represents a boolean; prepared as a python bool and cleaned as
    an actual bool in most deserializers.
    """

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


class IntegerAttribute(Attribute):
    """Represents an integer; serialzied as a python integer.
    """

    type = int

    def clean(self, value):
        if isinstance(value, six.string_types):
            # Strip the string of whitespace
            value = value.strip()

        if value is None:
            # Value is nothing; return it.
            return value

        try:
            # Attempt to coerce whatever we have as an int.
            return int(value)

        except ValueError:
            # Failed to do so.
            raise ValueError('Not a valid integer.')


try:
    # Attempt to import and make use of date/time libraries.
    # TODO: Make note of this optional dep somewhere.
    from dateutil.parser import parse as parse_datetime
    from time import mktime

except ImportError:
    # No support for date/times.
    parse_datetime = None


class _TemporalAttribute(object):
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
