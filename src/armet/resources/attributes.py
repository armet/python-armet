# -*- coding: utf-8 -*-
"""
Defines resource attribute objects encapsulating metadata of the
resource's attributes.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import six
from datetime import datetime
from time import mktime
from .. import utils
from . import helpers
from .proxy import find as find_proxy


def _find_relation(resource, path):
    """
    Take the related name and the path and attempt to figure out who
    we're related to.
    """
    if path[-1] in resource._resources:
        # There really is a resource out there.
        return resource._resources[path[-1]]

    else:
        # There may be a resource out there.
        try:
            if len(path) > 1:
                # Attempt to get the resource object in question
                resource = _find_relation(resource, path[:-1])

            # Try and get the actual field object here
            obj = resource._get_field_object(path[-1])

        except KeyError:
            # Didn't find it... die
            return None

        name = None
        try:
            # Attempt to find the name of the module for the related model.
            name = obj.rel.to._meta.module_name

        except AttributeError:
            # Didn't work.
            pass

        try:
            # Pretend this is a reverse or a direct foreign.
            name = obj.field.related.var_name

        except AttributeError:
            # Didn't find it; move along.
            pass

        try:
            # Pretend this is a normal m2m field.
            name = obj.m2m_reverse_field_name()

        except AttributeError:
            # Didn't find it; move along.
            pass

        if name is not None:
            # Attempt to retrieve the resource by its canonical name
            for resource in six.itervalues(resource._resources):
                if resource.model._meta.module_name == name:
                    return resource

class Attribute(object):

    def __init__(self, resource, **kwargs):
        #! The resource object this attribute is bound to.
        self.resource = resource

        #! Whether this attribute can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this attribute is a collection or not.
        self.collection = kwargs.get('collection', False)

        #! Whether this attribute may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! Visibility of the attribute.
        self.visible = kwargs.get('visible', False)

        #! Whether this attributes is bound to a model or not.
        self.model = kwargs.get('model', False)

        #! Accessor functions that will get the value of the attribute
        #! from a obj.
        self.accessors = kwargs.get('accessors', [])

        #! Preparation function that is linked to the class object of the
        #! instantiating resource.
        self.prepare = kwargs.get('prepare')

        #! Path of the attribute; storing for interesting purposes.
        self._path = self.path = kwargs.get('path')

        #! This attribute starts out possibly being related.
        self.relatable = True

        #! Stored relation reference
        self._relation = kwargs.get('relation')

    def _get_related_name(cls, resource, path):
        # I have no idea as a normal attribute..
        pass

    @property
    def relation(self):
        if self._relation is not None:
            if not isinstance(self._relation.resource, type):
                # Resolve resource class object.
                resource = utils.load(self._relation.resource)
                self._relation = self._relation._replace(resource=resource)

            if isinstance(self._relation.path, six.string_types):
                # Relation path needs to be expanded.
                path = self._relation.path.split('__')
                self._relation = self._relation._replace(path=path)

            if self._relation.related_name is None:
                # Related name needs to be discovered.
                name = self._get_related_name(self.resource, self.path)
                self._relation = self._relation._replace(related_name=name)

            # Resource class object is already resolved; return it.
            return self._relation

        elif self.relatable:
            if self.path:
                resource = _find_relation(self.resource, self.path)
                if resource is not None:
                    # We're related.. yay
                    name = self.resource._get_related_name(self.path[-1])

                    # Store it.
                    self._relation = helpers.relation(resource,
                        related_name=name)

                    # Let's do this again.
                    return self.relation

                else:
                    # We're not relatable
                    self.relatable = False

        # Nothing to relate; go away.

    def accessor(self, value):
        for accessor in self.accessors:
            # Iterate and access the entire attribute path
            value = accessor(value)

        if value is not None and self._path:
            depth = 0
            for segment in self._path:
                if value is None:
                    # If we don't have a value anymore; get out.
                    break

                # If additional accessors are needed; build them now
                accessor = self._build_accessor(value.__class__, segment)

                # Append the accessor
                self.accessors.append(accessor)

                # Use the accessor
                value = accessor(value)

                # Increment depth
                depth += 1

            # Remove segments used
            self._path = self._path[depth:]

        # Return what we've accessed
        return value

    def clean(self, value):
        """Cleans the value for consumption by the form clean cycle."""
        # Base attribute class just passes the value through.
        return value

    def _build_accessor(self, cls, name):
        # Determine proxy if we have one
        proxy = find_proxy(cls)
        if proxy is not None:
            # We have one; apply it.
            cls = proxy

        obj = getattr(cls, name, None)
        if obj is not None:
            if hasattr(obj, '__call__'):
                # A callable descriptor at the very least.
                return lambda o, x=obj.__call__: x(o)

            if hasattr(obj, '__get__'):
                # A readable descriptor at the very least.
                return lambda o, x=obj.__get__: x(o)

        if issubclass(cls, collections.Mapping):
            # Some kind of mapping; use dictionary access.
            return lambda o, n=name: o[name]

        if issubclass(cls, collections.Sequence):
            # Some kind of sequence; use item access.
            index = int(name)
            if index == 0:
                def accessor(obj):
                    # Can't index-0 into a 1-index'd string.
                    raise TypeError()

            else:
                index = index - 1 if index > 0 else index
                def accessor(obj, index=index):
                    if isinstance(obj, six.string_types) and len(obj) == 1:
                        # We cannot index into a character of 1.
                        raise TypeError

                    # Return the character or array element.
                    return obj[index]

            # Return the built accessor
            return accessor

        # No alternative; attempt direct attribute access using the instance
        # dictionary.
        return lambda o, n=name: o.__dict__[n]


class ModelAttribute(object):

    @classmethod
    def _get_related_name(cls, resource, path):
        if len(path) > 1:
            # Iterate and attempt to resolve the path down.
            resource = _find_relation(resource, path[:-1])

        if resource is None:
            # No resource provided; bail
            return None

        try:
            # Get the actual model field
            obj = resource.model_fields.get(path[-1])

        except AttributeError:
            # Something really weird.. resource has no model.
            return None

        try:
            # Pretend we have a reverse related object here.
            return obj.field.attname

        except AttributeError:
            # Didn't work.
            pass

        try:
            # Try for a many-to-many relation.
            return obj.field.m2m_field_name()

        except AttributeError:
            # Didn't work.
            pass

        try:
            # Try for a foreign key relation.
            return obj.related.var_name

        except AttributeError:
            # Didn't work.
            pass

        # No related name that we can find; return nothing.

    def _build_accessor(self, cls, name):
        obj = getattr(cls, name, None)
        if obj is not None:
            if hasattr(obj, 'related_manager_cls'):
                # Relation where it is a {1,*}-*
                return lambda o, x=obj.__get__: x(o).all()

        # No alternative; let the base take it.
        return super(ModelAttribute, self)._build_accessor(cls, name)


class BooleanAttribute(Attribute):

    #! Values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on'
        '1'
    )

    #! Values accepted for `False`.
    FALSE = (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    )

    def clean(self, value):
        if value.strip().lower() in self.TRUE:
            # Some sort of truthy value.
            return True

        if value.strip().lower() in self.FALSE:
            # Some sort of falsy value.
            return False

        # Neither true or false matches; return what we were given.
        return value


class TemporalAttribute(object):

    @staticmethod
    def _try(value):
        try:
            # Attempt to use the dateutil library to parse.
            from dateutil.parser import parse
            return parse(value, fuzzy=False)

        except ValueError:
            # Not a strictly formatted date; return nothing.
            pass

        try:
            import parsedatetime.parsedatetime as pdt
            import parsedatetime.parsedatetime_consts as pdc
            c = pdc.Constants()
            c.BirthdayEpoch = 80
            p = pdt.Calendar(c)
            result = p.parse(value)
            if result[1] != 0:
                return datetime.fromtimestamp(mktime(result[0]))

        except NameError:
            # No magic date/time support
            pass


class DateAttribute(Attribute, TemporalAttribute):

    def clean(self, value):
        result = self._try(value)
        if result is not None:
            # Return our new date/time
            return result.date()

        # We can't figure it out; pass it on.
        return value


class TimeAttribute(Attribute, TemporalAttribute):

    def clean(self, value):
        result = self._try(value)
        if result is not None:
            # Return our new date/time
            return result.time()

        # We can't figure it out; pass it on.
        return value


class DateTimeAttribute(Attribute, TemporalAttribute):

    def clean(self, value):
        result = self._try(value)
        if result is not None:
            # Return our new date/time
            return result

        # We can't figure it out; pass it on.
        return value


class FileAttribute(Attribute):
    pass
