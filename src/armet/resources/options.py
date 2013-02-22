# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
import collections
import six
from armet.resources.attributes import Attribute
from armet import utils


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


class ResourceOptions(object):

    @classmethod
    def _merge(cls, options, name, bases):
        """Merges a named option collection."""
        result = None
        for base in bases:
            if base is None:
                continue

            value = getattr(base, name, None)
            if value is None:
                continue

            result = utils.extend(result, value)

        value = options.get(name)
        if value is not None:
            result = utils.extend(result, value)

        return result

    def __init__(self, options, name, bases):
        """
        Initializes the options object and defaults configuration not
        specified.

        @param[in] options
            Dictionary of the merged options attributes.

        @param[in] name
            Name of the resource class this is being instantiataed for.
        """
        #! Name of the resource to use in URIs; defaults to the dasherized
        #! version of the camel cased class name (eg. SomethingHere becomes
        #! something-here). The defaulted version also strips a trailing
        #! Resource from the name (eg. SomethingHereResource still becomes
        #! something-here).
        self.name = options.get('name')
        if self.name is None:
          # Generate a name for the resource if one is not provided.
          # PascalCaseThis => pascal-case-this
          names = re.findall(r'[A-Z]?[a-z]+|[0-9]+/g', name)
          if len(names) > 1 and names[-1].lower() == 'resource':
              # Strip off a trailing Resource as well.
              names = names[:-1]
          self.name = '-'.join(names).lower()

        #! Connectors to use to connect to the environment.
        #!
        #! This is a dictionary that maps hooks (keys) to the connector to use
        #! for the hook.
        #!
        #! There is only 1 hook available currently, 'http', and it is required.
        #!
        #! The available connectors are as follows:
        #!  - http:
        #!      > django
        #!      > flask
        #!
        #! They may be used as follows:
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     connectors = {'http': 'django'}
        #! @endcode
        #!
        #! Connectors may also be specified as full paths to the connector
        #! module (if a connector is located somewhere other than
        #! armet.connectors) as follows:
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     connectors = {'http': 'some.other.place'}
        #! @endcode
        #!
        #! If connectors are not specified there is *some* auto-detection done
        #! to introspect your environment and determine the appropriate
        #! connectors. This *should* work for most.
        self.connectors = self._merge(options, 'connectors', bases)

        if not self.connectors.get('http'):
            # Attempt to detect the HTTP connector
            self.connectors['http'] = _detect_connector_http()

        if not self.connectors['http']:
            raise ImproperlyConfigured(
                'No HTTP connector was detected; available connectors are:'
                'django and flask')

        # Pull out the connectors and convert them into module references.
        for connector_name in self.connectors:
            connector = self.connectors[connector_name]
            if '.' not in connector:
                # Shortname, prepend base.
                self.connectors[connector_name] = 'armet.connectors.{}'.format(
                    connector)

        #! Additional attributes to include in addition to those defined
        #! directly in the resource. This is meant for defining fields
        #! with names that conflict with names used in the resource as
        #! methods. This could be used exclusively; it's a matter of
        #! preference.
        #!
        #! Attributes may also be declared shorthand in a few different
        #! ways. The next few code blocks are identical in function.
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     name = attributes.Attribute()
        #!     created = attributes.Attribute('created')
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = {
        #!             'name': attributes.Attribute()
        #!             'created': attributes.Attribute('created')
        #!         }
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = {
        #!             'name': None,
        #!             'created': 'created'
        #!         }
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = ('name',)
        #!     created = attributes.Attribute('created')
        #! @endcode
        self.include = options.get('include', {})
        if not isinstance(self.include, collections.Mapping):
            if isinstance(self.include, collections.Iterable):
                # This is a list, tuple, etc. but not a dictionary.
                self.include = {name: Attribute() for name in self.include}

        else:
            # This is a dictionary; normalize it.
            for key, value in six.iteritems(self.include):
                if isinstance(value, six.string_types) or value is None:
                    self.include[key] = Attribute(value)
