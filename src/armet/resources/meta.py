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
from django.db.models.fields.files import FileField
from django.forms import FileField as FormFileField
from django.db.models.fields.related import RelatedField
from django.db.models.related import RelatedObject
from .. import utils
from .helpers import attribute as field_helper
from . import attributes, link


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


def _collect_dict(name, attrs, bases):
    """Merges the hashes for all bases plus the current class."""
    value = {}
    if name in attrs and attrs[name] is not None:
        value.update(**attrs[name])

    for base in bases:
        if name in base.__dict__ and base.__dict__[name] is not None:
            value.update(**base.__dict__[name])

    return value


def _collect_list(name, attrs, bases):
    """Merges the lists for all bases plus the current class."""
    value = []
    if name in attrs and attrs[name] is not None:
        value.extend(attrs[name])

    for base in bases:
        if name in base.__dict__ and base.__dict__[name] is not None:
            value.extend(base.__dict__[name])

    return value


def _config(self, name, config, attrs, bases):
    """Overrides a property by a config option if it isn't specified."""
    if not _has(name, attrs, bases):
        options = utils.config(config)
        if options is not None:
            setattr(self, name, options)


def _is_field_visible(obj, name):
    """Checks for the visibility in displaying of the attribute."""
    visible = not (obj.attributes and name not in obj.attributes)
    visible = visible and (not (obj.exclude and name in obj.exclude))
    return visible


def _is_field_editable(obj, name):
    """Checks if the attribute is declared to be editable."""
    visible = not (obj.fields and name not in obj.fields)
    visible = visible and (not (obj.exclude and name in obj.exclude))
    return visible


def _is_field_filterable(obj, name):
    """Checks if the specified attribute is declared to be filterable."""
    return not (obj.filterable and name not in obj.filterable)


def _is_field_collection(field):
    """Tests if the specified attribute is some type of collection."""
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


def _is_field_related(field):
    return isinstance(field, (RelatedObject, RelatedField))


def _method_to_operation(method):
    if method == 'GET':
        return set(['read'])

    if method == 'PUT':
        return set(['update', 'create', 'delete'])

    if method == 'POST':
        return set(['create'])

    if method == 'PATCH':
        return set(['update', 'create'])

    if method == 'DELETE':
        return set(['destory'])


def _methods_to_operations(methods):
    operations = set()
    for method in operations:
        operations = operations.union(_method_to_operation(method))

    return operations


def _operation_to_method(operation):
    if operation == 'read':
        return set(['GET'])

    if operation == 'update':
        return set(['PUT', 'PATCH'])

    if operation == 'create':
        return set(['PUT', 'PATCH', 'POST'])

    if operation == 'destroy':
        return set(['PUT', 'DELETE'])


def _operations_to_methods(operations):
    methods = set(['HEAD', 'OPTIONS'])
    for operation in operations:
        methods = methods.union(_operation_to_method(operation))

    return methods


def _get_field_class(field):
    """Determines what class object to instantiate for the specified field."""
    if field is None:
        # No attribute passed; return the base class
        return attributes.Attribute

    if _is_field_related(field):
        # This is actually a related field or object.
        return attributes.Attribute

    try:
        # Attempt to handle file streams
        test = StringIO()
        if (field.to_python(test).getvalue() == ''
                or isinstance(field, FileField)
                or isinstance(field, FormFileField)):
            # Looks like we're capable of dealing with file streams
            return attributes.FileAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # File streams cannot be handled
        pass

    try:
        # Attempt to handle numbers
        test = 78647848
        if field.to_python(test) == test:
            # Looks like we're a numbers attribute
            return attributes.NumericalAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle date/times
        test = datetime.datetime.now()
        if field.to_python(test) == test:
            # Looks like we're a datetime attribute
            return attributes.DateTimeAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle times
        test = datetime.datetime.now().time()
        if field.to_python(test) == test:
            # Looks like we're a time field
            return attributes.TimeAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # Times cannot be handled.
        pass

    try:
        # Attempt to handle dates
        test = datetime.datetime.now().date()
        if field.to_python(test) == test:
            # Looks like we're a date field
            return attributes.DateAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # Dates cannot be handled.
        pass

    try:
        # Attempt to handle booleans
        test = True
        if field.to_python(test) is True:
            # Looks we can explicitly handle booleans
            return attributes.BooleanAttribute

    except (forms.ValidationError, AttributeError, TypeError, ValueError):
        # Booleans cannot be handled
        pass

    # We have no idea what we are; assume we're just text
    return attributes.Attribute


class DeclarativeResource(type):
    """Defines the metaclass for the Resource class.
    """

    def _get_field_object(self, name):
        try:
            # Check the form attribute dictionary for the attribute object
            return self.form_fields[name]

        except KeyError:
            # Not a form attribute; return nothing.
            pass

    def _get_field_class(self, attribute):
        # Attempt to get the attribute class using the declared attribute.
        return _get_field_class(attribute)

    def _get_related_name(self, name):
        # Attempt to get the related name for the indiciated attribute.
        pass

    def _set_attribute(
            self,
            name,
            path=None,
            collection=None,
            editable=None,
            attribute=None,
            cls=None,
            related_name=None):
        """Sets the attribute with the passed name on the resource."""
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
            # Attempt to get the attribute object.
            attribute = self._get_field_object(parts[0])

        else:
            # No path parts; no attribute.
            attribute = None

        # Get the attribute class to use.
        cls = self._get_field_class(attribute)

        # Conditionally determine some attribute properites.
        if editable is None:
            if hasattr(self.form, '_meta') and parts:
                # If a value for editable was not provided; discover it
                editable = _is_field_editable(self.form._meta, parts[0])

            else:
                # No black/white list on form; its editable if it happens to
                # be on the form.
                editable = parts[0] in self.form_fields if parts else False

        if collection is None:
            if attribute:
                # We have a attribute; figure it out
                collection = _is_field_collection(attribute)

            else:
                # No value was provided for collection; it isn't one
                collection = False

        try:
            # Attempt to get the prepare_FOO function for the attribute by name
            prepare = getattr(self, 'prepare_{}'.format(name))

        except AttributeError:
            # No prepare_FOO function; make a no-op one.
            prepare = lambda s, o, v, n=name: s.generic_prepare(o, n, v)
            setattr(self, 'prepare_{}'.format(name), prepare)

        # Pull the relation and attempt to determine the related name if
        # not provided.
        relation = self.relations.get(name)
        if relation is not None:
            if relation.related_name is None:
                relation = relation._replace(
                    related_name=self._get_related_name(parts[0]))

        # Instantiate the attribute object and set it on the resource class.
        self._attributes[name] = cls(
            self,
            visible=_is_field_visible(self, name),
            filterable=_is_field_filterable(self, name),
            collection=collection,
            editable=editable,
            prepare=prepare,
            path=parts,
            relation=relation
        )

    def _discover_attributes(self):
        """
        Finds all attributes declared on the class object and collects them
        into a dictionary.
        """
        # Discover any attributes we can.
        # If the resource has a form we need to discover its attributes.
        if self.form is not None:
            # Iterate through explicitly defined attributes to gather their
            # properites and store them.
            for name in self.form_fields:
                # If a attribute has been explicitly defined; according to
                # the django forms protocol it is -always- editable --
                # regardless of whatever the black/white lists on the
                # form state.
                self._set_attribute(name, path=[name], editable=True)

        # Append any 'extra' attributes listed in the `include` directive.
        if self.include is not None:
            # Iterate through additional attribute names and set them.
            for name in self.include:
                path, collection = self.include[name]
                self._set_attribute(
                    name,
                    path=path.split('__') if path is not None else None,
                    collection=collection)

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(DeclarativeResource, self).__init__(
                name, bases, attrs)

        for base in bases:
            if base.__name__ == 'NewBase':
                # This is a six contrivance; move along
                continue

            if isinstance(base, DeclarativeResource):
                # This is some sort of derived resource; good
                break

        else:
            # There isn't a single resource that is derived from another
            # resource in the bases lists. This is the root resource object.
            return super(DeclarativeResource, self).__init__(
                name, bases, attrs)

        if (self.include is not None
                and not isinstance(self.include, collections.Mapping)):
            # Simple form was used; make a simple dictionary to
            # ease processing.
            self.include = {n: field_helper() for n in self.include}

            # Update attrs listing for include.
            attrs['include'] = self.include

        # Collect and merge all hashes for `include` and `relations`
        self.include = _collect_dict('include', attrs, bases)
        self.relations = _collect_dict('relations', attrs, bases)
        self.list_links = _collect_list('list_links', attrs, bases)
        self.detail_links = _collect_list('detail_links', attrs, bases)

        # Initialize our ordered attributes dictionary.
        self._attributes = collections.OrderedDict()

        if self.form is not None:
            # Ensure this is a valid form; attempt to instantiate one.
            self.form()

            # If the form has a `declared_attributes` attribute then that is
            # whatwould normally be at `base_attributes`; else
            # `base_attributes` is the list of explicitly defined attributes.
            self.form_fields = self.form.base_fields
            if hasattr(self.form, 'declared_fields'):
                self.form_fields = self.form.declared_fields

        else:
            # No form; no form attributes; make us an empty dictionary.
            self.form_fields = {}

        # Discover any attributes we can.
        self._discover_attributes()

        # Ensure the resource has a name.
        # PascalCaseThis => pascal_case_this
        if 'name' not in attrs:
            import re
            names = re.findall('[A-Z]?[a-z]+|[0-9]+/g', name)
            self.name = '_'.join(names).lower()

        # Unless `filterable` was explicitly provided in a class object,
        # default `filterable` to an empty tuple.
        if not _has('filterable', attrs, bases):
            self.filterable = ()

        # Ensure that detail and list allowed methods and operations are as
        # synced up as possible
        # FIXME: This could be a nice loop I suppose
        if not _has('http_allowed_methods', attrs, bases):
            if _has('allowed_operations', attrs, bases):
                self.http_allowed_methods = _operations_to_methods(
                    self.allowed_operations)

        elif not _has('allowed_operations', attrs, bases):
            self.allowed_operations = _methods_to_operations(
                self.http_allowed_methods)

        # Ensure list and detail allowed methods and operations are populated.
        for fmt, default in (
                ('http_{}_allowed_methods', self.http_allowed_methods),
                ('{}_allowed_operations', self.allowed_operations)):
            for key in ('list', 'detail'):
                attr = fmt.format(key)
                if not _has(attr, attrs, bases):
                    setattr(self, attr, default)

        if not _has('http_detail_allowed_methods', attrs, bases):
            if _has('detail_allowed_operations', attrs, bases):
                self.http_detail_allowed_methods = _operations_to_methods(
                    self.detail_allowed_operations)

        elif not _has('detail_allowed_operations', attrs, bases):
            self.detail_allowed_operations = _methods_to_operations(
                self.http_detail_allowed_methods)

        if not _has('http_list_allowed_methods', attrs, bases):
            if _has('list_allowed_operations', attrs, bases):
                self.http_list_allowed_methods = _operations_to_methods(
                    self.list_allowed_operations)

        elif not _has('list_allowed_operations', attrs, bases):
            self.list_allowed_operations = _methods_to_operations(
                self.http_list_allowed_methods)

        # Add the allowed headers for a list.
        if not _has('http_list_allowed_headers', attrs, bases):
            setattr(self, 'http_list_allowed_headers',
                    self.http_allowed_headers)

        # Add the allowed headers for a detail.
        if not _has('http_detail_allowed_headers', attrs, bases):
            setattr(self, 'http_detail_allowed_headers',
                    self.http_allowed_headers)

        # Add the exposed headers for a list.
        if not _has('http_list_exposed_headers', attrs, bases):
            setattr(self, 'http_list_exposed_headers',
                    self.http_exposed_headers)

        # Add the exposed headers for a detail.
        if not _has('http_detail_exposed_headers', attrs, bases):
            setattr(self, 'http_detail_exposed_headers',
                    self.http_exposed_headers)

        # Add the allowed origins for a list.
        if not _has('list_allowed_origins', attrs, bases):
            setattr(self, 'list_allowed_origins',
                    self.allowed_origins)

        # Add the allowed origins for a detail.
        if not _has('detail_allowed_origins', attrs, bases):
            setattr(self, 'detail_allowed_origins',
                    self.allowed_origins)

        # Override properties that can be provided by configuration options
        # if we should.
        _config(self, 'url_name', 'url', attrs, bases)
        _config(self, 'http_method_names', 'http.methods', attrs, bases)
        _config(self, 'encoders', 'encoders', attrs, bases)
        _config(self, 'default_encoder', 'default.encoder', attrs, bases)
        _config(self, 'decoders', 'decoders', attrs, bases)
        _config(
            self,
            'authentication',
            'resource.authentication',
            attrs,
            bases
        )

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

        # Find and store all `prepare_FOO` functions on attributes for fast
        # access.
        for name in self._attributes:
            prepare = 'prepare_{}'.format(name)
            if hasattr(self, prepare):
                self._attributes[name].prepare = getattr(self, prepare)

        # Let's get it cracking!
        # Store anything accessed frequently through `getattr` on the cls
        # object.
        self._resolver = urlresolvers.get_resolver(urlresolvers.get_urlconf())
        self._prefix = urlresolvers.get_script_prefix()

        # Finish us up.
        super(DeclarativeResource, self).__init__(name, bases, attrs)


class DeclarativeModel(DeclarativeResource):

    #! Cache of canonical resources.
    _resources = {}

    #! Cache of prefetchable attributes.
    _prefetchable = True

    def _get_field_object(self, name):
        try:
            # Check the model attribute dictionary for the attribute object
            return self.model_fields[name]

        except KeyError:
            # Not a model attribute; perhaps..
            return super(DeclarativeModel, self)._get_field_object(name)

    def _get_field_class(self, attribute):
        # Attempt to get the attribute class using the declared attribute.
        attribute = super(DeclarativeModel, self)._get_field_class(attribute)

        # Meld with a Model Field
        # TODO: Remove `b` prefix upon python3
        attribute = type(
            b'Model{}'.format(attribute.__name__),
            (attributes.ModelAttribute, attribute),
            {}
        )

        # Return what we got
        return attribute

    def _discover_attributes(self):
        # Iterate through and set these model attributes on the resource.
        for name in self.model_fields:
            # Grab the attribute object
            attribute = self.model_fields[name]

            if isinstance(attribute, RelatedObject):
                # Don't automagically generate reverse relationships.
                continue

            # Set the attribute on the resource.
            self._set_attribute(name, path=name)

        # Discover any additional attributes.
        super(DeclarativeModel, self)._discover_attributes()

    def __init__(self, name, bases, attrs):
        if name == 'NewBase':
            # Six contrivance; we don't care
            return super(DeclarativeModel, self).__init__(name, bases, attrs)

        if (self.form is None or self.form.__name__ == 'armet:Form') and self.model is not None:
            # Create a model form automatically if none exists
            class Meta:
                model = self.model
            Form = type(b'armet:Form', (forms.ModelForm,), {'Meta': Meta})

            # Assign our new model form
            self.form = Form

        # Discover what we can from the model form.
        if self.form is not None and issubclass(self.form, forms.ModelForm):
            # Store the model from the form.
            self.model = self.form._meta.model

        if self.model:
            # Store the model attributes.
            self.model_fields = {}
            for field_name in self.model._meta.get_all_field_names():
                # Get attribute object from the model
                attribute = self.model._meta.get_field_by_name(field_name)[0]

                # We store these by accessor name and not neccessarily by
                # attribute name.
                accessor = field_name

                # Touch up if we're a reverse relation as things are stored
                # a bit differently.
                if isinstance(attribute, RelatedObject):
                    accessor = attribute.get_accessor_name()

                # Store these in our dictionary.
                self.model_fields[accessor] = attribute

        else:
            # No model; no model attributes: store an empty dictionary.
            self.model_fields = {}

        # Ensure the resource has a name.
        if 'name' not in attrs:
            self.name = name.lower()

        if self.canonical and self.model is not None:
            if self.name in self._resources:
                # Already exists somewhere.
                raise ImproperlyConfigured(
                    'A canonical resource already exists for the'
                    ' linked model.')

            # Designate this as a canonical resource for the linked model.
            self._resources[self.name] = self

        # Discover anything else we can from the form
        super(DeclarativeModel, self).__init__(name, bases, attrs)
