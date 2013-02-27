# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
import collections
import six
import pkgutil
from importlib import import_module
import os
from armet.resources.attributes import Attribute
from armet import utils


def _detect_connector(*capacities):
    """Auto-detect available connectors."""
    for module in utils.iter_modules(import_module('armet.connectors')):
        if module.is_available(*capacities):
            return module.__name__


def _merge(options, name, bases, default=None):
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

    return result or default


class ResourceOptions(object):


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
            dashed = utils.dasherize(name).strip()
            if dashed:
                # Strip off a trailing Resource as well.
                self.name = re.sub(r'-resource$', '', dashed)

            else:
                # Something went wrong; just use the class name
                self.name = name

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
        self.connectors = connectors = _merge(options, 'connectors', bases, {})

        if not connectors.get('http'):
            # Attempt to detect the HTTP connector
            connectors['http'] = _detect_connector('http')

        if not connectors['http']:
            raise ImproperlyConfigured('No valid HTTP connector was detected.')

        # Pull out the connectors and convert them into module references.
        for key in connectors:
            connector = connectors[key]
            if '.' not in connector:
                # Shortname, prepend base.
                connectors[key] = 'armet.connectors.{}'.format(connector)

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
        self.include = include = options.get('include', {})
        if not isinstance(include, collections.Mapping):
            # This is a list, tuple, etc. but not a dictionary.
            self.include = {name: Attribute() for name in include}

        else:
            # This is a dictionary; normalize it.
            for key, value in six.iteritems(include):
                if value is None or isinstance(value, six.string_types):
                    include[key] = Attribute(value)
