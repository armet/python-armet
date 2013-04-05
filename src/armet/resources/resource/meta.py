# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet import utils
from armet.resources.attributes import Attribute
from . import options


#! Map of connector class objects in their connector modules.
CONNECTORS = {
    'http': {
        'resource': ('{}.resources', 'Resource',),
        'options': ('{}.resources', 'ResourceOptions',)
    },
    'model': {
        'resource': ('{}.resources', 'ModelResource',),
        'options': ('{}.resources', 'ModelResourceOptions',)
    }
}


class ResourceBase(type):

    #! Options class to use to expand options.
    options = options.ResourceOptions

    @classmethod
    def _is_resource(cls, name, bases):
        if name == 'NewBase':
            # This is a six contrivance; not a real class.
            return False

        if name.startswith('armet.connector:'):
            # This is special mixed connector class; not something
            # to run the metaclass over.
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

        # Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Iterate through the available connectors.
        iterator = six.iteritems(meta.connectors)
        connectors = []
        cmap = CONNECTORS
        for key, ref in iterator:
            options = utils.import_module(cmap[key]['options'][0].format(ref))
            if options:
                options = getattr(options, cmap[key]['options'][1], None)
                if options:
                    # Available options to parse for this connector;
                    # instantiate the options class and apply all
                    # available options.
                    options_instance = options(metadata, name, base_meta)
                    meta.__dict__.update(**options_instance.__dict__)

            module = utils.import_module(cmap[key]['resource'][0].format(ref))
            if module:
                klass = getattr(module, cmap[key]['resource'][1], None)
                if klass:
                    # Found a connector class for this connector
                    connectors.append(klass)

        # Mix all the connector types together.
        connectors.append(self)
        connectors = tuple(connectors)
        combined = type(b'armet.connector:{}'.format(name), connectors, {})

        # Return the constructed instance.
        return combined
