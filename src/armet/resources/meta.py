# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from armet import exceptions
from armet.resources import options


class ResourceBase(type):

    #! Options class to use to expand options.
    options = options.ResourceOptions

    @staticmethod
    def _detect_connector_http():
        """Auto-detect HTTP connector."""
        try:
            # Attempted import
            import django

            # Now try and use it
            from django.conf import settings
            settings.DEBUG

            # HTTP connector looks like its django
            return 'django'

        except:
            # Failed to import django; or, we don't have a proper settings
            # file.
            pass

        try:
            # Attempted import
            import flask

            # TODO: Add additional checks to assert that flask is actually
            #   in use.

            # Detected connector.
            return 'flask'

        except ImportError:
            pass

        # Couldn't figure it out...
        return None

    @staticmethod
    def _is_resource(name, bases):
        if name == 'NewBase':
            # This is a six contrivance; not a real class.
            return False

        for base in bases:
            if base.__name__ == 'NewBase':
                # This is a six contrivance; move along.
                continue

            if isinstance(base, ResourceBase):
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
        meta = attrs['meta'] = cls.options(metadata, name)

        # Get the value of the least derived connectors object.
        connectors = getattr(meta, 'connectors', {})

        if not connectors.get('http'):
            # Attempt to detect the HTTP connector
            connectors['http'] = cls._detect_connector_http()

        if not connectors['http']:
            raise ImproperlyConfigured(
                'No HTTP connector was detected; available connectors are:'
                'django and flask')

        # Pull out the connectors and convert them into module references.
        for connector_name in connectors:
            connector = connectors[connector_name]
            if '.' not in connector:
                # Shortname, prepend base.
                connectors[connector_name] = 'armet.connectors.{}'.format(
                    connector)

        # Store the expanded connectors
        meta.connectors = connectors

        # Apply the HTTP connector.
        # Mangle the bases. Note that this does not actually change the bases
        # in posterity, it only changes the bases at class object creation.
        # The significance here is that class may derive and change their
        # connectors.
        connector = import_module('{}.resources'.format(connectors['http']))
        new_bases = []
        for base in bases:
            if base is not import_module('armet.resources').Resource:
                new_bases.append(base)

            else:
                new_bases.append(connector.Resource)

        #! Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, tuple(new_bases),
            attrs)

        #! Return the constructed object.
        return self

    # def __init__(self, name, bases, attrs):
    #     # Initialize the class.
    #     super(ResourceBase, self).__init__(name, bases, attrs)

    #     if not self._is_resource(name, bases):
    #         # This is not an actual resource.
    #         return

    #     # Invoke the initialize hook.
    #     self.initialize(name, bases, attrs)

    # def initialize(self, name, bases, attrs):
    #     """
    #     Initialize is invoked only under the following conditions:
    #         - The class is not NewBase (six contrivance)
    #         - The class is dervied from Resource (its not the root class)

    #     @note This is the method to overload with additional metaclass
    #         functionality.
    #     """
