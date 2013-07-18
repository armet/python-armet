# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import collections
from armet.resources.attributes import Attribute
from ..resource.meta import ResourceBase
from . import options


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

        # Append include directives here
        attributes.update(self.meta.include)

        # Ensure all attributes are unique instances.
        for attr in attributes:
            attributes[attr] = attributes[attr].clone()

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

        # Return the constructed class object.
        return self
