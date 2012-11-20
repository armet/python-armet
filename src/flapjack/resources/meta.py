# -*- coding: utf-8 -*-
"""Defines the metaclasses used to instantiate the resource classes.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import datetime
import collections
from StringIO import StringIO
from django.db.models import RelatedObject
from django import forms
import six
from .. import utils, fields


def _has(name, attrs, bases):
    """
    Determines if a property has been expliclty specified by this or a
    base class.
    """
    if name in attrs:
        # Attribute is explicitly declared on the class object.
        return attrs[name] is not None

    for base in bases:
        if name in base.__dict__:
            # Attribute has been declared explicitly in a base class.
            return base.__dict__[name] is not None

    # No attribute; tough luck.
    return False


def _config(self, name, config, attrs, bases):
    """Overrides a property by a config option if it isn't specified."""
    if not _has(name, attrs, bases):
        options = utils.config(config)
        if options is not None:
            setattr(self, name, options)


def _is_field_visible(obj, name):
    """Checks for the visibility in displaying of the field."""
    visible = not (obj.fields and name not in obj.fields)
    visible = visible and (not (obj.exclude and name in obj.exclude))
    return visible


def _is_field_editable(obj, name):
    """Checks if the field is declared to be editable."""
    visible = not (obj.fields and name not in obj.fields)
    visible = visible and (not (obj.exclude and name in obj.exclude))
    return visible


def _is_field_filterable(obj, name):
    """Checks if the specified field is declared to be filterable."""
    return not (obj.filterable and name not in obj.filterable)


def _is_field_iterable(obj, field):
    """Tests if the specified field is some type of iterable."""
    try:
        # Attempt to discover if the null value is some sort of
        # iterable (and isn't a string) which would make it an iterable.
        null = field.to_python(None)
        return (isinstance(null, collections.Iterable)
            and not isinstance(null, six.string_types))

    except forms.ValidationError:
        # None cannot be a valid value; definitely not an iterable.
        return False


def _get_field_class(self, field):
    """Determines what class object to instantiate for the specified field."""
    try:
        # Attempt to handle date/times
        test = datetime.datetime.now()
        if field.to_python(test) == test:
            # Looks like we're a datetime field
            return fields.DateTimeField

    except forms.ValidationError:
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle times
        test = datetime.datetime.now().time()
        if field.to_python(test) == test:
            # Looks like we're a time field
            return fields.TimeField

    except forms.ValidationError:
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle dates
        test = datetime.datetime.now().date()
        if field.to_python(test) == test:
            # Looks like we're a date field
            return fields.DateField

    except forms.ValidationError:
        # Dates cannot be handled.
        pass

    try:
        # Attempt to handle file streams
        test = StringIO()
        field.to_python(test)

        # Looks like we're capable of dealing with file streams
        return fields.FileField

    except forms.ValidationError:
        # File streams cannot be handled
        pass

    try:
        # Attempt to handle booleans
        test = True
        if field.to_python(test) is True:
            # Looks we can explicitly handle booleans
            return fields.BooleanField

    except forms.ValidationError:
        # Booleans cannot be handled
        pass

    # We have no idea what we are; assume were just text
    return fields.Field


class Resource(type):
    """
    """

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(Resource, self).__init__(name, bases, attrs)

        # Initialize our ordered fields dictionary.
        self._fields = collections.OrderedDict()

        # If the resource has a form we need to discover its fields.
        if self.form is not None:
            # Ensure this is a valid form; attempt to instantiate one.
            self.form()

            # If the form is a `ModelForm` and has a model; discover and
            # collect its fields.
            if isinstance(self.form, forms.ModelForm):
                for name in self.form._meta.get_all_field_names():
                    field = self.form._meta.get_field_by_name(name)

                    if isinstance(field, RelatedObject):
                        # If a field is a related object then this was
                        # generated because of a reverse relation and some
                        # special modifications to the properties need
                        # to happen
                        iterable = field.field.rel.multiple
                        accessor = field.get_accessor_name()
                        field = field.field

                    else:
                        # Seemingly normal field; proceed.
                        iterable = _is_field_iterable(field)
                        accessor = name

                    # Instantiate and store field with its properties
                    self._fields[name] = _get_field_class(field)(accessor,
                        visible=_is_field_visible(name),
                        filterable=_is_field_filterable(name),
                        iterable=iterable,
                        editable=_is_field_editable(self.form._meta, name))

            # If the form has a `declared_fields` attribute then that is what
            # would normally be at `base_fields`; else `base_fields` is the
            # list of explicitly defined fields.
            declared_fields = self.form.base_fields
            if hasattr(self.form, 'declared_fields'):
                declared_fields = self.form.declared_fields

            # Iterate through explicitly defined fields to gather their
            # properites and store them.
            for name in declared_fields:
                field = declared_fields[name]
                self._fields[name] = _get_field_class(field)(name,
                    visible=_is_field_visible(name),
                    filterable=_is_field_filterable(name),
                    iterable=_is_field_iterable(field),

                    # If a field has been explicitly defined; according to
                    # the django forms protocol it is -always- editable --
                    # regardless of whatever the black/white lists on the
                    # form state.
                    editable=True)

        # TODO: Append any 'extra' fields listed in the `include` directive.

        # Ensure the resource has a name.
        if 'name' not in attrs:
            self.name = name.lower()

        # Unless `filterable` was explicitly provided in a class object,
        # default `filterable` to an empty tuple.
        if not self._has('filterable', attrs, bases):
            self.filterable = ()

        # Ensure list and detail allowed methods and operations are populated.
        for fmt, default in (
                    ('http_{}_allowed_methods', self.http_allowed_methods),
                    ('{}_allowed_operations', self.allowed_operations),
                ):
            for key in ('list', 'detail'):
                attr = fmt.format(key)
                if not self._has(attr, attrs, bases):
                    setattr(self, attr, default)

        # Override properties that can be provided by configuration options
        # if we should.
        self._config('url_name', 'url', attrs, bases)
        self._config('http_method_names', 'http.methods', attrs, bases)
        self._config('encoders', 'encoders', attrs, bases)
        self._config('default_encoder', 'default.encoder', attrs, bases)
        self._config('decoders', 'decoders', attrs, bases)
        self._config('authentication', 'resource.authentication', attrs, bases)

        # Ensure properties are inflated the way they need to be.
        for_all = utils.for_all
        test = lambda x: isinstance(x, six.string_types)
        method = lambda x: x()
        for name in (
                    'encoders',
                    'decoders',
                    'authentication',
                ):
            # Ensure certain properties that may be name qualified instead of
            # class objects are resolved to be class objects.
            setattr(self, name, for_all(getattr(self, name), utils.load, test))

            # Ensure things that need to be instantied are instantiated.
            setattr(self, name, for_all(getattr(self, name), method, callable))


class Model(Resource):
    pass
