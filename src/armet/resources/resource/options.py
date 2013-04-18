# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import re
import six
from importlib import import_module
from armet import utils
from armet.exceptions import ImproperlyConfigured


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

        result = utils.cons(result, value)

    value = options.get(name)
    if value is not None:
        result = utils.cons(result, value)

    return result or default


class ResourceOptions(object):

    def __init__(self, meta, name, bases):
        """
        Initializes the options object and defaults configuration not
        specified.

        @param[in] meta
            Dictionary of the merged meta attributes.

        @param[in] name
            Name of the resource class this is being instantiataed for.
        """
        #! Name of the resource to use in URIs; defaults to the dasherized
        #! version of the camel cased class name (eg. SomethingHere becomes
        #! something-here). The defaulted version also strips a trailing
        #! Resource from the name (eg. SomethingHereResource still becomes
        #! something-here).
        self.name = meta.get('name')
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
        #! There is only 1 hook available currently, 'http', and it is
        #! required.
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
        self.connectors = connectors = _merge(meta, 'connectors', bases, {})

        if not connectors.get('http'):
            # Attempt to detect the HTTP connector
            connectors['http'] = _detect_connector('http')

        if not connectors['http']:
            raise ImproperlyConfigured('No valid HTTP connector was detected.')

        # Pull out the connectors and convert them into module references.
        for key in connectors:
            connector = connectors[key]
            if isinstance(connector, six.string_types):
                if '.' not in connector:
                    # Shortname, prepend base.
                    connectors[key] = 'armet.connectors.{}'.format(connector)

        #! Trailing slash handling.
        #! The value indicates which URI is the canonical URI and the
        #! alternative URI is then made to redirect (with a 301) to the
        #! canonical URI.
        self.trailing_slash = meta.get('trailing_slash', True)

        #! List of understood HTTP methods.
        self.http_method_names = meta.get('http_method_names', (
            'HEAD',
            'OPTIONS',
            'GET',
            'POST',
            'PUT',
            'PATCH',
            'DELETE',
        ))

        #! List of allowed HTTP methods.
        #! If not provided and allowed_operations was provided instead
        #! the operations are appropriately mapped; else, the default
        #! configuration is provided.
        self.http_allowed_methods = meta.get('http_allowed_methods')
        if self.http_allowed_methods is None:
            self.http_allowed_methods = (
                'HEAD',
                'OPTIONS',
                'GET',
                'POST',
                'PUT',
                'PATCH',
                'DELETE',
            )

        #! Whether to use legacy redirects or not to inform the
        #! client the resource is available elsewhere. Legacy redirects
        #! require a combination of 301 and 307 in which 307 is not cacheable.
        #! Modern redirecting uses 308 and is in effect 307 with cacheing.
        #! Unfortunately unknown 3xx codes are treated as
        #! a 300 (Multiple choices) in which the user is supposed to chose
        #! the alternate link so the client is not supposed to auto follow
        #! redirects. Ensure all supported clients understand 308 before
        #! turning off legacy redirecting.
        #! As of 19 March 2013 only Firefox supports it since a year ago.
        self.legacy_redirect = meta.get('legacy_redirect', True)

        #! Mapping of encoders known by this resource.
        #! Values may either be a string reference to the encoder type
        #! or an encoder class object.
        self.encoders = encoders = meta.get('encoders')
        if not encoders:
            self.encoders = {
                'json': 'armet.encoders.JsonEncoder'
            }

        # Check to ensure at least one encoder is defined.
        if len(self.encoders) == 0:
            raise ImproperlyConfigured(
                'At least one available encoder must be defined.')

        # Expand the encoder name references.
        for name, encoder in six.iteritems(self.encoders):
            if isinstance(encoder, six.string_types):
                segments = encoder.split('.')
                module = '.'.join(segments[:-1])
                module = import_module(module)
                self.encoders[name] = getattr(module, segments[-1])

        #! List of allowed encoders of the understood encoders.
        self.allowed_encoders = meta.get('allowed_encoders')
        if not self.allowed_encoders:
            self.allowed_encoders = tuple(self.encoders.keys())

        # Check to ensure at least one encoder is allowed.
        if len(self.allowed_encoders) == 0:
            raise ImproperlyConfigured(
                'There must be at least one allowed encoder.')

        # Check to ensure that all allowed encoders are understood encoders.
        for name in self.allowed_encoders:
            if name not in self.encoders:
                raise ImproperlyConfigured(
                    'The allowed encoder, {}, is not one of the '
                    'understood encoders'.format(name))

        #! Name of the default encoder of the list of understood encoders.
        self.default_encoder = meta.get('default_encoder')
        if not self.default_encoder:
            if 'json' in self.allowed_encoders:
                self.default_encoder = 'json'

            else:
                self.default_encoder = self.allowed_encoders[0]

        if self.default_encoder not in self.allowed_encoders:
            raise ImproperlyConfigured(
                'The chosen default encoder, {}, is not one of the '
                'allowed encoders'.format(self.default_encoder))
