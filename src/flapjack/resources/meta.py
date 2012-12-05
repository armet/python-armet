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
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject
from .. import utils
from .helpers import field as field_helper
from . import fields


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


def _collect(name, attrs, bases):
    """Merges the hashes for all bases plus the current class."""
    value = {}
    if name in attrs and attrs[name] is not None:
        value.update(**attrs[name])

    for base in bases:
        if name in base.__dict__ and base.__dict__[name] is not None:
            value.update(**base.__dict__[name])

    return value


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


def _is_field_collection(field):
    """Tests if the specified field is some type of collection."""
    if isinstance(field, RelatedObject):
        # This happens to be a reverse relation; test using the provided.
        return field.field.rel.multiple

    try:
        # Attempt to discover if the null value is some sort of
        # collection (and isn't a string) which would make it an collection.
        null = field.to_python(None)
        return (isinstance(null, collections.Iterable)
                and not isinstance(null, six.string_types))

    except forms.ValidationError:
        # None cannot be a valid value; definitely not an collection.
        return False


def _get_field_class(field):
    """Determines what class object to instantiate for the specified field."""
    if field is None:
        # No field passed; return the base class
        return fields.Field

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

    def _get_field_object(self, name):
        try:
            # Check the form field dictionary for the field object
            return self.form_fields[name]

        except KeyError:
            # Not a form field; return nothing.
            pass

    def _get_field_class(self, field):
        # Attempt to get the field class using the declared field.
        return _get_field_class(field)

    def _set_field(self,
            name,
            path=None,
            collection=None,
            editable=None,
            field=None,
            cls=None):
        """Sets the field with the passed name on the resource."""
        if isinstance(path, six.string_types):
            # Explode the segments from the path
            parts = path.split('__') if path is not None else ('')

        else:
            # Already exploded.
            parts = path

        if parts is not None and not parts[0]:
            # If there is no valid segment#0 then the name becomes segment#0.
            parts[0] = name

        if parts is not None:
            # Attempt to get the field object.
            field = self._get_field_object(parts[0])

        else:
            # No path parts; no field.
            field = None

        # Get the field class to use.
        cls = self._get_field_class(field)

        # Conditionally determine some field properites.
        if editable is None:
            if hasattr(self.form, '_meta') and parts:
                # If a value for editable was not provided; discover it
                editable = _is_field_editable(self.form._meta, parts[0])

            else:
                # No black/white list on form; its editable if it happens to
                # be on the form.
                editable = parts[0] in self.form_fields if parts else False

        if collection is None:
            if field:
                # We have a field; figure it out
                collection = _is_field_collection(field)

            else:
                # No value was provided for collection; it isn't one
                collection = False

        try:
            # Attempt to get the prepare_FOO function for the field by name.
            prepare = getattr(self, 'prepare_{}'.format(name))

        except AttributeError:
            # No prepare_FOO function; make a no-op one.
            prepare = lambda s, o, v, n=name: s.generic_prepare(o, n, v)
            setattr(self, 'prepare_{}'.format(name), prepare)

        # Instantiate the field object and set it on the resource class.
        self._fields[name] = cls(
            visible=_is_field_visible(self, name),
            filterable=_is_field_filterable(self, name),
            collection=collection,
            editable=editable,
            prepare=prepare,
            path=parts,
            relation=self.relations.get(name)
        )

    def _discover_fields(self):
        """
        Finds all fields declared on the class object and collects them
        into a dictionary.
        """
        # Discover any fields we can.
        # If the resource has a form we need to discover its fields.
        if self.form is not None:
            # Iterate through explicitly defined fields to gather their
            # properites and store them.
            for name in self.form_fields:
                # If a field has been explicitly defined; according to
                # the django forms protocol it is -always- editable --
                # regardless of whatever the black/white lists on the
                # form state.
                self._set_field(name, editable=True)

        # Append any 'extra' fields listed in the `include` directive.
        if self.include is not None:
            # Iterate through additional field names and set them.
            for name in self.include:
                path, collection = self.include[name]
                self._set_field(name,
                    path=path.split('__') if path is not None else None,
                    collection=collection)

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(DeclarativeResource, self).__init__(
                name, bases, attrs)\

        if (self.include is not None
                and not isinstance(self.include, collections.Mapping)):
            # Simple form was used; make a simple dictionary to
            # ease processing.
            self.include = {n: field_helper() for n in self.include}

            # Update attrs listing for include.
            attrs['include'] = self.include

        # Collect and merge all hashes for `include` and `relations`
        self.include = _collect('include', attrs, bases)
        self.relations = _collect('relations', attrs, bases)

        # Initialize our ordered fields dictionary.
        self._fields = collections.OrderedDict()

        if self.form is not None:
            # Ensure this is a valid form; attempt to instantiate one.
            self.form()

            # If the form has a `declared_fields` attribute then that is what
            # would normally be at `base_fields`; else `base_fields` is the
            # list of explicitly defined fields.
            self.form_fields = self.form.base_fields
            if hasattr(self.form, 'declared_fields'):
                self.form_fields = self.form.declared_fields

        else:
            # No form; no form fields; make us an empty dictionary.
            self.form_fields = {}

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

        # Finish us up.
        super(DeclarativeResource, self).__init__(name, bases, attrs)


class DeclarativeModel(DeclarativeResource):

    def _get_field_object(self, name):
        try:
            # Check the model field dictionary for the field object
            return self.model_fields[name]

        except KeyError:
            # Not a model field; perhaps..
            return super(DeclarativeModel, self)._get_field_object(name)

    def _get_field_class(self, field):
        # Attempt to get the field class using the declared field.
        field = super(DeclarativeModel, self)._get_field_class(field)

        # Meld with a Model Field
        # TODO: Remove `b` prefix upon python3
        field = type(b'Model{}'.format(field.__name__),
            (fields.ModelField, field), {})

        # Return what we got
        return field

    def _discover_fields(self):
        # Iterate through and set these model fields on the resource.
        for name in self.model_fields:
            # Grab the field object
            field = self.model_fields[name]

            if isinstance(field, RelatedObject):
                # Don't automagically generate reverse relationships.
                continue

            # Set the field on the resource.
            self._set_field(name, path=name)

        # Discover any additional fields.
        super(DeclarativeModel, self)._discover_fields()

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(DeclarativeModel, self).__init__(name, bases, attrs)

        # Discover what we can from the model form.
        if self.form is not None and issubclass(self.form, forms.ModelForm):
            # Store the model from the form.
            self.model = self.form._meta.model

        if self.model:
            # Store the model fields.
            self.model_fields = {}
            for field_name in self.model._meta.get_all_field_names():
                # Get field object from the model
                field = self.model._meta.get_field_by_name(field_name)[0]

                # We store these by accessor name and not neccessarily by
                # field name.
                accessor = field_name

                # Touch up if we're a reverse relation as things are stored
                # a bit differently.
                if isinstance(field, RelatedObject):
                    accessor =  field.get_accessor_name()

                # Store these in our dictionary.
                self.model_fields[accessor] = field

        else:
            # No model; no model fields: store an empty dictionary.
            self.model_fields = {}

        # Discover anything else we can from the form
        super(DeclarativeModel, self).__init__(name, bases, attrs)

        # Declare class object caches; every resource needs one of these
        self._prefetch_related_paths = []
