# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import armet
from collections import OrderedDict
from armet import utils
from . import options


#! Map of connector class objects in their connector modules.
CONNECTORS = OrderedDict([
    ('http', {
        'resource': ('{}.resources', 'Resource', 'resource.base',),
        'options': ('{}.resources', 'ResourceOptions',)
    }),
    ('model', {
        'resource': ('{}.resources', 'ModelResource', 'model.base',),
        'options': ('{}.resources', 'ModelResourceOptions',)
    })
])


#! Set of connector classes.
connector_set = set()


def apply_connectors(meta, name, bases, metadata, base_meta):

    # Apply the declared connectors. What this entails is inserting the
    # connector base classes at the correct location in the base class list.

    # The correct location would be directly before one of the base resource
    # classes.

    # What is not implemented (and will not be) is replacing existing
    # connectors. You may have an inheritance chain of as many "abstract"
    # resources as warranted but as soon as a connector is supplied on a
    # non-abstract resource then that connector is "locked-in" so-to-speak.

    # Order the connectors found in meta by the order declared above.
    connectors = OrderedDict()
    for key in reversed(CONNECTORS):
        if key in meta.connectors:
            connectors[key] = meta.connectors[key]

    meta.connectors = connectors

    # Iterate through the declared connectors.
    cmap = CONNECTORS
    new_bases = list(bases)
    offset = 0
    for key, ref in six.iteritems(meta.connectors):

        try:
            # Resolve an optional options class that may be provided by
            # the connector.
            options = utils.import_module(cmap[key]['options'][0].format(ref))
            options = getattr(options, cmap[key]['options'][1])
            options_instance = options(metadata, name, base_meta)
            meta.__dict__.update(**options_instance.__dict__)

        except (AttributeError, KeyError):
            pass

        try:
            # Resolve the connector itself.
            module = utils.import_module(cmap[key]['resource'][0].format(ref))
            class_ = getattr(module, cmap[key]['resource'][1], None)

            # Ensure the connector has not already been applied.
            applied = False
            for base in bases:
                if issubclass(base, class_):
                    applied = True

            if applied:
                continue

            # Find where to insert this connector.
            module_key = 'armet.resources.%s' % cmap[key]['resource'][2]
            module = utils.import_module(module_key)
            armet_resource = getattr(module, cmap[key]['resource'][1])
            for index, base in enumerate(bases):
                if issubclass(base, armet_resource):
                    new_bases.insert(index + offset, class_)
                    offset += 1
                    break

        except (AttributeError, KeyError):
            pass

    return tuple(new_bases)


class ResourceBase(type):

    #! Options class to use to expand options.
    options = options.ResourceOptions

    #! Connectors to instantiate and mixin to the inheritance.
    connectors = ['http']

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

        # This is not derived at all from Resource (eg. is base).
        return False

    @classmethod
    def _gather_metadata(cls, metadata, bases):
        for base in bases:
            if isinstance(base, cls) and hasattr(base, 'Meta'):
                # Append metadata.
                metadata.append(getattr(base, 'Meta'))

                # Recurse.
                cls._gather_metadata(metadata, base.__bases__)

    def __new__(cls, name, bases, attrs):
        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Gather the attributes of all options classes.
        # Start with the base configuration.
        metadata = armet.use().copy()
        values = lambda x: {n: getattr(x, n) for n in dir(x)}

        # Expand the options class with the gathered metadata.
        base_meta = []
        cls._gather_metadata(base_meta, bases)

        # Apply the configuration from each class in the chain.
        for meta in base_meta:
            metadata.update(**values(meta))

        cur_meta = {}
        if attrs.get('Meta'):
            # Apply the configuration from the current class.
            cur_meta = values(attrs['Meta'])
            metadata.update(**cur_meta)

        # Gather and construct the options object.
        meta = attrs['meta'] = cls.options(metadata, name, cur_meta, base_meta)

        # Apply the found connectors.
        bases = apply_connectors(meta, name, bases, metadata, base_meta)

        # Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Generate a serializer map that maps media ranges to serializer
        # names.
        self._serializer_map = smap = {}
        for key in self.meta.allowed_serializers:
            serializer = self.meta.serializers[key]
            for media_type in serializer.media_types:
                smap[media_type] = key

        # Generate a deserializer map that maps media ranges to deserializer
        # names.
        self._deserializer_map = dmap = {}
        for key in self.meta.allowed_deserializers:
            deserializer = self.meta.deserializers[key]
            for media_type in deserializer.media_types:
                dmap[media_type] = key

        # Filter the available connectors according to the
        # metaclass restriction set.
        for key in list(meta.connectors.keys()):
            if key not in cls.connectors:
                del meta.connectors[key]

        # Return the constructed instance.
        return self
