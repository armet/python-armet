# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import collections
from armet.exceptions import ImproperlyConfigured
from armet.attributes import Attribute
from ..resource.meta import ResourceBase
from armet.relationship import Relationship
from . import options
import copy


class ManagedResourceBase(ResourceBase):

    options = options.ManagedResourceOptions

    def __new__(cls, name, bases, attrs):
        # Construct the class object.
        self = super(ManagedResourceBase, cls).__new__(cls, name, bases, attrs)

        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return self

        # Gather declared attributes from ourself and base classes.
        # TODO: We'll likely need a hook here for ORMs
        self.attributes = attributes = collections.OrderedDict()
        for base in bases:
            if getattr(base, 'attributes', None):
                attributes.update(base.attributes)

        for index, attribute in six.iteritems(attrs):
            if isinstance(attribute, Attribute):
                attributes[index] = attribute

        # Ensure all attributes are unique instances and assign names.
        # This is done so that when attributes are resolved; the resolution
        # cache does not clobber base resources (for inherited attributes).
        for attr in attributes:
            attributes[attr] = attributes[attr].clone()
            if not attributes[attr].name:
                attributes[attr].name = attr

        # Resolve the slug reference to an attribute.
        if self.meta.slug not in attributes:
            if not self.meta.abstract:
                raise ImproperlyConfigured(
                    'slug must reference an existing attribute')

        else:
            self.meta.slug = attributes[self.meta.slug]

        # Cache access to the attribute preparation cycle.
        self.preparers = preparers = {}
        for key in attributes:
            prepare = getattr(self, 'prepare_{}'.format(key), None)
            if not prepare:
                prepare = lambda self, obj, value: value
            preparers[key] = prepare

        # Cache access to the attribute clean cycle.
        self.cleaners = cleaners = {}
        for key in attributes:
            clean = getattr(self, 'clean_{}'.format(key), None)
            if not clean:
                clean = lambda self, value: value
            cleaners[key] = clean

        # Collect all relationships and store them by their model key.
        self.relationships = relationships = collections.OrderedDict()
        for base in bases:
            if getattr(base, 'relationships', None):
                relationships.update(base.relationships)

        for name, attr in six.iteritems(attrs):
            if isinstance(attr, Relationship):
                relationships[name] = attr

        # Ensure all relationships are unique instances.
        for attr in relationships:
            relationships[attr] = copy.copy(relationships[attr])

        # Return the constructed class object.
        return self
