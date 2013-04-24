# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import armet
from armet import utils
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

    #! Connectors to instantiate and mixin to the inheritance.
    connectors = ['http']

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, sub):
        mro = sub.mro()
        if cls in mro:
            return True
        return any(b in mro for b in cls.__bases__)

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
        # Start with the base configuration.
        metadata = armet.use()
        values = lambda x: {n: getattr(x, n) for n in dir(x)}
        for base in bases:
            meta = getattr(base, 'Meta', None)
            if meta:
                # Apply the configuration from each class in the chain.
                metadata.update(**values(meta))

        if attrs.get('Meta'):
            # Apply the configuration from the current class.
            metadata.update(**values(attrs['Meta']))

        # Expand the options class with the gathered metadata.
        base_meta = [getattr(b, 'Meta') for b in bases if hasattr(b, 'Meta')]
        meta = attrs['meta'] = cls.options(metadata, name, base_meta)

        # Remove connector layer from base classes.
        new_bases = []
        for base in bases:
            if base.__name__.startswith('armet.connector:'):
                # This is a connector wrapper; unwrap it.
                new_bases.append(base.__bases__[-1])
            else:
                # Not a connector wrapped object; just append it.
                new_bases.append(base)
        new_bases = tuple(new_bases)

        # Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, new_bases, attrs)

        # Generate a serializer map that maps media ranges to serializer
        # names.
        self._serializer_map = smap = {}
        for key in self.meta.allowed_serializers:
            serializer = self.meta.serializers[key]
            for media_type in serializer.media_types:
                smap[media_type] = key

        # Filter the available connectors according to the
        # metaclass restriction set.
        for key in list(meta.connectors.keys()):
            if key not in cls.connectors:
                del meta.connectors[key]

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
        name = 'armet.connector:{}'.format(name)
        combined = type(str(name), connectors, {})

        # Return the constructed instance.
        return combined
