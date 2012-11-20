# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import datetime
from StringIO import StringIO
import six
from django import forms
from django.core import urlresolvers
from django.db.models.related import RelatedObject
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


def _is_field_iterable(field):
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


def _get_field_class(field):
    """Determines what class object to instantiate for the specified field."""
    try:
        # Attempt to handle date/times
        test = datetime.datetime.now()
        if field.to_python(test) == test:
            # Looks like we're a datetime field
            return fields.DateTimeField

    except (forms.ValidationError, AttributeError):
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle times
        test = datetime.datetime.now().time()
        if field.to_python(test) == test:
            # Looks like we're a time field
            return fields.TimeField

    except (forms.ValidationError, AttributeError):
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle dates
        test = datetime.datetime.now().date()
        if field.to_python(test) == test:
            # Looks like we're a date field
            return fields.DateField

    except (forms.ValidationError, AttributeError):
        # Dates cannot be handled.
        pass

    try:
        # Attempt to handle file streams
        test = StringIO()
        field.to_python(test)

        # Looks like we're capable of dealing with file streams
        return fields.FileField

    except (forms.ValidationError, AttributeError):
        # File streams cannot be handled
        pass

    try:
        # Attempt to handle booleans
        test = True
        if field.to_python(test) is True:
            # Looks we can explicitly handle booleans
            return fields.BooleanField

    except (forms.ValidationError, AttributeError):
        # Booleans cannot be handled
        pass

    # We have no idea what we are; assume we're just text
    return fields.Field


class DeclarativeResource(type):
    """Defines the metaclass for the Resource class.
    """

    def _discover_fields(self):
        # If the resource has a form we need to discover its fields.
        if self.form is not None:
            # Ensure this is a valid form; attempt to instantiate one.
            self.form()

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
                    visible=_is_field_visible(self, name),
                    filterable=_is_field_filterable(self, name),
                    iterable=_is_field_iterable(field),

                    # If a field has been explicitly defined; according to
                    # the django forms protocol it is -always- editable --
                    # regardless of whatever the black/white lists on the
                    # form state.
                    editable=True)

        # TODO: Append any 'extra' fields listed in the `include` directive.

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(DeclarativeResource, self).__init__(
                name, bases, attrs)

        # Initialize our ordered fields dictionary.
        self._fields = collections.OrderedDict()

        # Discover any fields we can.
        self._discover_fields()

        # Ensure the resource has a name.
        if 'name' not in attrs:
            self.name = name.lower()

        # Unless `filterable` was explicitly provided in a class object,
        # default `filterable` to an empty tuple.
        if not _has('filterable', attrs, bases):
            self.filterable = ()

        # Ensure list and detail allowed methods and operations are populated.
        for fmt, default in (
                ('http_{}_allowed_methods', self.http_allowed_methods),
                ('{}_allowed_operations', self.allowed_operations)):
            for key in ('list', 'detail'):
                attr = fmt.format(key)
                if not _has(attr, attrs, bases):
                    setattr(self, attr, default)

        # Override properties that can be provided by configuration options
        # if we should.
        _config(self, 'url_name', 'url', attrs, bases)
        _config(self, 'http_method_names', 'http.methods', attrs, bases)
        _config(self, 'encoders', 'encoders', attrs, bases)
        _config(self, 'default_encoder', 'default.encoder', attrs, bases)
        _config(self, 'decoders', 'decoders', attrs, bases)
        _config(self, 'authentication', 'resource.authentication',
            attrs, bases)

        # Ensure properties are inflated the way they need to be.
        for_all = utils.for_all
        test = lambda x: isinstance(x, six.string_types)
        method = lambda x: x()
        for name in (
                'encoders',
                'decoders',
                'authentication'):
            # Ensure certain properties that may be name qualified instead of
            # class objects are resolved to be class objects.
            setattr(self, name, for_all(getattr(self, name), utils.load, test))

            # Ensure things that need to be instantied are instantiated.
            setattr(self, name, for_all(getattr(self, name), method, callable))

        # Find and store all `prepare_FOO` functions on fields for fast
        # access.
        for name in self._fields:
            prepare = 'prepare_{}'.format(name)
            if hasattr(self, prepare):
                self._fields[name].prepare = getattr(self, prepare)

        # Let's get it cracking!
        # Store anything accessed frequently through `getattr` on the cls
        # object.
        self._resolver = urlresolvers.get_resolver(urlresolvers.get_urlconf())
        self._prefix = urlresolvers.get_script_prefix()

class DeclarativeModel(DeclarativeResource):

    def _discover_fields(self):
        # Discover what we can from the model form.
        if self.form is not None and issubclass(self.form, forms.ModelForm):
            model = self.form._meta.model
            for name in model._meta.get_all_field_names():
                field = model._meta.get_field_by_name(name)[0]

                if isinstance(field, RelatedObject):
                    # If a field is a related object then this was
                    # generated because of a reverse relation and some
                    # special modifications to the properties need
                    # to happen
                    iterable = field.field.rel.multiple
                    field_name = field.get_accessor_name()
                    field = field.field
                    accessor = \
                        lambda o, x=getattr(model, field_name): x(o).all()

                else:
                    # Seemingly normal field; proceed.
                    iterable = _is_field_iterable(field)
                    field_name = name
                    accessor = lambda o, n=name: o.__dict__[n]

                # Instantiate and store field with its properties
                self._fields[name] = _get_field_class(field)(field_name,
                    visible=_is_field_visible(self, name),
                    filterable=_is_field_filterable(self, name),
                    iterable=iterable,
                    editable=_is_field_editable(self.form._meta, name),
                    model=True,
                    accessor=accessor)

        # Discover anything else we can from the form
        super(DeclarativeModel, self)._discover_fields()
