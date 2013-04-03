# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from armet.resources.attributes import Attribute
from . import options


class ResourceBase(type):

    #! Options class to use to expand options.
    options = options.ResourceOptions

    @classmethod
    def _is_resource(cls, name, bases):
        if name == 'NewBase':
            # This is a six contrivance; not a real class.
            return False

        for base in bases:
            if base.__name__ == 'NewBase':
                # This is a six contrivance; move along.
                continue

            if isinstance(base, cls):
                # This is some sort of derived resource; good.
                return True

        # This is not derived at all from Resource (eg. is Resource)
        return False

    def __new__(cls, name, bases, attrs):
        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Gather the attributes of all options classes.
        metadata = {}
        for base in bases:
            meta = getattr(base, 'Meta', None)
            if meta:
                metadata.update(**meta.__dict__)

        if attrs.get('Meta'):
            metadata.update(**attrs['Meta'].__dict__)

        # Expand the options class with the gathered metadata.
        base_meta = [getattr(b, 'Meta') for b in bases if hasattr(b, 'Meta')]
        meta = attrs['meta'] = cls.options(metadata, name, base_meta)

        # Apply the HTTP connector.
        # Mangle the bases. Note that this does not actually change the bases
        # in posterity, it only changes the bases at class object creation.
        # The significance here is that class may derive and change their
        # connectors.
        connector = import_module('{}.resources'.format(
            meta.connectors['http']))

        new_bases = []
        for base in bases:
            if base is not import_module('armet.resources').Resource:
                new_bases.append(base)

            else:
                new_bases.append(connector.Resource)

        new_bases = tuple(new_bases)

        # Gather declared attributes from ourself and base classes.
        # TODO: We'll likely need a hook here for ORMs
        attributes = {}
        for base in bases:
            if hasattr(base, 'attributes'):
                attributes.update(**base.attributes)

        for index, attribute in six.iteritems(attrs):
            if isinstance(attribute, Attribute):
                attributes[index] = attribute

        # Append include directives here
        attributes.update(**meta.include)

        # Store the gathered attributes
        attrs['attributes'] = attributes

        # Construct and return the constructed class object.
        return super(ResourceBase, cls).__new__(cls, name, new_bases, attrs)
