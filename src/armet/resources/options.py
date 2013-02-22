# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re


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

    def __init__(self, options, name):
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
        self.connectors = options.get('options', {})

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
