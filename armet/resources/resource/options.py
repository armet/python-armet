# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import re
import six
from importlib import import_module
from armet import utils, authentication, authorization
from armet.exceptions import ImproperlyConfigured
from armet import connectors as included_connectors


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

    def __init__(self, meta, name, data, bases):
        """
        Initializes the options object and defaults configuration not
        specified.

        @param[in] meta
            Dictionary of the merged meta attributes.

        @param[in] name
            Name of the resource class this is being instantiataed for.
        """
        #! Whether to allow display of debugging information
        #! to the client.
        self.debug = meta.get('debug')
        if self.debug is None:
            self.debug = False

        #! Whether to not actualize a resource from the described class.
        #! Abstract resources are meant as generic base classes.
        #!
        #! @note
        #!      Abstract only counts if it is directly set on the resource.
        self.abstract = data.get('abstract')

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

        elif callable(self.name):
            # If name is callable; pass in the class name and use what
            # we got back.
            self.name = self.name(name)

        #! True if the resource is expected to operate asynchronously.
        #!
        #! The side-effect of setting this to True is that returning from
        #! `dispatch` (and by extension `get`, `post`, etc.) does not
        #! terminate the connection. You must invoke `response.close()` to
        #! terminate the connection.
        self.asynchronous = meta.get('asynchronous', False)

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
        #!     class Meta:
        #!         connectors = {'http': 'django'}
        #! @endcode
        #!
        #! Connectors may also be specified as full paths to the connector
        #! module (if a connector is located somewhere other than
        #! armet.connectors) as follows:
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         connectors = {'http': 'some.other.place'}
        #! @endcode
        self.connectors = connectors = _merge(meta, 'connectors', bases, {})

        if not connectors.get('http') and not self.abstract:
            raise ImproperlyConfigured('No valid HTTP connector was detected.')

        # Pull out the connectors and convert them into module references.
        for key in connectors:
            connector = connectors[key]
            if isinstance(connector, six.string_types):
                if connector in getattr(included_connectors, key):
                    # Included shortname; prepend base.
                    connectors[key] = 'armet.connectors.{}'.format(connector)

        #! Additional options to handle and merge into the meta object
        #! at the class object level.
        #!
        #! This should be a simple set/list/tuple of options.
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         options = {'color', 'plant'}
        #!
        #! @endcode
        self.options = options = _merge(meta, 'options', bases, {})
        for name in options:
            # Pull out each option and stick it on the meta.
            setattr(self, name, meta.get(name))

        #! Regular-expression patterns to apply to the request path
        #! and pull arguments and traversal out of it.
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         patterns = [
        #!             # Match nothing after the resource name.
        #!             r'^$',
        #!
        #!             # Match a slug after the resource name.
        #!             r'^/(?P<slug>[^/]+)/?$',
        #!         ]
        #!
        #! @endcode
        #!
        #! Named parameters get auto-attached to `self` on the resource
        #! instance.
        #!
        #! This may be a list of lists/tuples as well to indicate simple
        #! traversal.
        #!
        #! @code
        #! from armet import resources
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         patterns = [
        #!             # Match nothing and don't traverse.
        #!             (None, r'^$'),
        #!
        #!             # Match the word 'user' and traverse.
        #!             # The remainder of the path is taken or
        #!             # the named gruop, "path" (if the whole path was
        #!             # matched) or the last-matched group (if none are
        #!             # named "path")
        #!             (UserResource, r'^/user'),
        #!         ]
        #!
        #! @endcode
        self.patterns = meta.get('patterns', [])
        for index, pattern in enumerate(self.patterns):
            # Coerce simple form.
            if isinstance(pattern, six.string_types):
                pattern = (None, pattern)

            # Compile the expression.
            self.patterns[index] = (pattern[0], re.compile(pattern[1]))

        #! Trailing slash handling.
        #! The value indicates which URI is the canonical URI and the
        #! alternative URI is then made to redirect (with a 301) to the
        #! canonical URI.
        self.trailing_slash = meta.get('trailing_slash', True)

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

        #! List of allowed HTTP headers.
        #! This is used only to request or prevent CORS requests.
        self.http_allowed_headers = meta.get('http_allowed_headers')
        if self.http_allowed_headers is None:
            self.http_allowed_headers = (
                'Content-Type',
                'Authorization',
                'Accept',
                'Origin'
            )

        #! List of exposed HTTP headers.
        #! This is used only to show headers to the client.
        self.http_exposed_headers = meta.get('http_exposed_headers')
        if self.http_exposed_headers is None:
            self.http_exposed_headers = (
                'Content-Type',
                'Authorization',
                'Accept',
                'Origin'
            )

        #! List of allowed HTTP origins.
        #! This is used to request or prevent CORS requests.
        #! No CORS requests will be allowed, at-all, unless this
        #! property is set.
        #! NOTE: This can be set to '*' to indicate any origin.
        self.http_allowed_origins = meta.get('http_allowed_origins')
        if self.http_allowed_origins is None:
            self.http_allowed_origins = ()

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

        #! Mapping of serializers known by this resource.
        #! Values may either be a string reference to the serializer type
        #! or an serializer class object.
        self.serializers = serializers = meta.get('serializers')
        if not serializers:
            self.serializers = {
                'json': 'armet.serializers.JSONSerializer',
                'url': 'armet.serializers.URLSerializer'
            }

        # Expand the serializer name references.
        for name, serializer in six.iteritems(self.serializers):
            if isinstance(serializer, six.string_types):
                segments = serializer.split('.')
                module = '.'.join(segments[:-1])
                module = import_module(module)
                self.serializers[name] = getattr(module, segments[-1])

        #! List of allowed serializers of the understood serializers.
        self.allowed_serializers = meta.get('allowed_serializers')
        if not self.allowed_serializers:
            self.allowed_serializers = tuple(self.serializers.keys())

        # Check to ensure that all allowed serializers are
        # understood serializers.
        for name in self.allowed_serializers:
            if name not in self.serializers:
                raise ImproperlyConfigured(
                    'The allowed serializer, {}, is not one of the '
                    'understood serializers'.format(name))

        #! Name of the default serializer of the list of
        #! understood serializers.
        self.default_serializer = meta.get('default_serializer')
        if not self.default_serializer:
            if 'json' in self.allowed_serializers:
                self.default_serializer = 'json'

            else:
                self.default_serializer = self.allowed_serializers[0]

        if self.default_serializer not in self.allowed_serializers:
            raise ImproperlyConfigured(
                'The chosen default serializer, {}, is not one of the '
                'allowed serializers'.format(self.default_serializer))

        #! Mapping of deserializers known by this resource.
        #! Values may either be a string reference to the deserializer type
        #! or an deserializer class object.
        self.deserializers = deserializers = meta.get('deserializers')
        if not deserializers:
            self.deserializers = {
                'json': 'armet.deserializers.JSONDeserializer',
                'url': 'armet.deserializers.URLDeserializer'
            }

        # Expand the deserializer name references.
        for name, deserializer in six.iteritems(self.deserializers):
            if isinstance(deserializer, six.string_types):
                segments = deserializer.split('.')
                module = '.'.join(segments[:-1])
                module = import_module(module)
                self.deserializers[name] = getattr(module, segments[-1])

        #! List of allowed deserializers of the understood deserializers.
        self.allowed_deserializers = meta.get('allowed_deserializers')
        if not self.allowed_deserializers:
            self.allowed_deserializers = tuple(self.deserializers.keys())

        # Check to ensure that all allowed deserializers are
        # understood deserializers.
        for name in self.allowed_deserializers:
            if name not in self.deserializers:
                raise ImproperlyConfigured(
                    'The allowed deserializer, {}, is not one of the '
                    'understood deserializers'.format(name))

        #! List of authentication protocols to attempt in sequence
        #! to determine the authenticated user.
        self.authentication = meta.get('authentication')
        if self.authentication is None:
            # Default to a single instance of pass-through authentication.
            self.authentication = (authentication.Authentication(),)

        #! The authorization protocol to attempt to use
        #! to determine the if the user can access or is otherwise
        #! authorized.
        self.authorization = meta.get('authorization')
        if self.authorization is None:
            # Default is the pass-through authorization.
            self.authorization = authorization.Authorization()
