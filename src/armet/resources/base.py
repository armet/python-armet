# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
import six
from importlib import import_module
from armet import exceptions


class ResourceBase(type):

    @staticmethod
    def _has(name, bases, attrs):
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

    @staticmethod
    def _get(name, bases, attrs, default=None):
        """
        Retreives a property that has been expliclty specified by this or a
        base class.
        """
        if name in attrs:
            # Attribute is explicitly declared on the class object.
            return attrs[name]

        for base in bases:
            if hasattr(base, name):
                # Attribute has been declared on a base class.
                return getattr(base, name)

        # No attribute; tough luck.
        return default

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

        # Get the value of the least derived connectors object.
        connectors = cls._get('connectors', bases, attrs, {})

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

        # Apply the HTTP connector.
        # Mangle the bases. Note that this does not actually change the bases
        # in posterity, it only changes the bases at class object creation.
        # The significance here is that class may derive and change their
        # connectors.
        connector = import_module('{}.resources'.format(connectors['http']))
        new_bases = []
        for base in bases:
            if base is not Resource:
                new_bases.append(base)

            else:
                new_bases.append(connector.Resource)

        #! Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, tuple(new_bases),
            attrs)

        #! Return the constructed object.
        return self

    def __init__(self, name, bases, attrs):
        # Initialize the class.
        super(ResourceBase, self).__init__(name, bases, attrs)

        if not self._is_resource(name, bases):
            # This is not an actual resource.
            return

        # Invoke the initialize hook.
        self.initialize(name, bases, attrs)

    def initialize(self, name, bases, attrs):
        """
        Initialize is invoked only under the following conditions:
            - The class is not NewBase (six contrivance)
            - The class is dervied from Resource (its not the root class)

        @note This is the method to overload with additional metaclass
            functionality.
        """

        # Generate a name for the resource if one is not provided.
        if 'name' not in attrs:
            # PascalCaseThis => pascal-case-this
            names = re.findall(r'[A-Z]?[a-z]+|[0-9]+/g', name)
            if len(names) > 1 and names[-1].lower() == 'resource':
                # Strip off a trailing Resource as well.
                names = names[:-1]
            self.name = '-'.join(names).lower()


class Resource(six.with_metaclass(ResourceBase, object)):
    """Implements the RESTful resource protocol for abstract resources.
    """

    #! Name of the resource to use in URIs; defaults to the dasherized
    #! version of the camel cased class name (eg. SomethingHere becomes
    #! something-here). The defaulted version also strips a trailing Resource
    #! from the name (eg. SomethingHereResource still becomes something-here).
    name = None

    def __init__(self, **kwargs):
        """Initializes the resources and sets its properites."""
        pass

    def dispatch(self):
        return self.name
