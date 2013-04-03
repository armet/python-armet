# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
import collections
import six
from importlib import import_module
from armet.resources.attributes import Attribute
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

        result = utils.extend(result, value)

    value = options.get(name)
    if value is not None:
        result = utils.extend(result, value)

    return result or default


def _method_to_operation(method):
    if method == 'GET':
        return set(['read'])

    if method == 'PUT':
        return set(['update', 'create', 'delete'])

    if method == 'POST':
        return set(['create'])

    if method == 'PATCH':
        return set(['update', 'create'])

    if method == 'DELETE':
        return set(['destory'])


def _methods_to_operations(methods):
    operations = set()
    for method in operations:
        operations = operations.union(_method_to_operation(method))

    return operations


def _operation_to_method(operation):
    if operation == 'read':
        return set(['GET'])

    if operation == 'update':
        return set(['PUT', 'PATCH'])

    if operation == 'create':
        return set(['PUT', 'PATCH', 'POST'])

    if operation == 'destroy':
        return set(['PUT', 'DELETE'])


def _operations_to_methods(operations):
    methods = set(['HEAD', 'OPTIONS'])
    for operation in operations:
        methods = methods.union(_operation_to_method(operation))

    return methods


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
        self.include = include = meta.get('include', {})
        if not isinstance(include, collections.Mapping):
            # This is a list, tuple, etc. but not a dictionary.
            self.include = {name: Attribute() for name in include}

        else:
            # This is a dictionary; normalize it.
            for key, value in six.iteritems(include):
                if value is None or isinstance(value, six.string_types):
                    include[key] = Attribute(value)

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
            'CONNECT',
            'TRACE',
        ))

        #! List of allowed HTTP methods.
        #! If not provided and allowed_operations was provided instead
        #! the operations are appropriately mapped; else, the default
        #! configuration is provided.
        self.http_allowed_methods = meta.get('http_allowed_methods')
        if self.http_allowed_methods is None:
            if meta.get('allowed_operations'):
                self.http_allowed_methods = _operations_to_methods(meta.get(
                    'allowed_operations'))

            else:
                self.http_allowed_methods = (
                    'HEAD',
                    'OPTIONS',
                    'GET',
                    'POST',
                    'PUT',
                    'PATCH',
                    'DELETE',
                )

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the
        #! differences between "PATCH and PUT", "PUT = create / update",
        #! etc.
        #!
        #! If not provided and http_allowed_methods was provided instead
        #! the methods are appropriately mapped; else, the default
        #! configuration is provided.
        self.allowed_operations = meta.get('allowed_operations')
        if self.allowed_operations is None:
            if meta.get('http_allowed_methods'):
                self.allowed_operations = _methods_to_operations(meta.get(
                    'http_allowed_methods'))

            else:
                self.allowed_operations = (
                    'read',
                    'create',
                    'update',
                    'destroy',
                )

        #! List of allowed HTTP methods against a whole
        #! resource (eg /user); if undeclared or None, will be defaulted
        #! to `http_allowed_methods`.
        self.http_list_allowed_methods = meta.get(
            'http_list_allowed_methods')

        if self.http_list_allowed_methods is None:
            if meta.get('list_allowed_operations'):
                self.http_list_allowed_methods = _operations_to_methods(
                    meta.get('list_allowed_operations'))

            else:
                self.http_list_allowed_methods = self.http_allowed_methods

        #! List of allowed HTTP methods against a single
        #! resource (eg /user/1); if undeclared or None, will be defaulted
        #! to `http_allowed_methods`.
        self.http_detail_allowed_methods = meta.get(
            'http_detail_allowed_methods')

        if self.http_detail_allowed_methods is None:
            if meta.get('detail_allowed_operations'):
                self.http_detail_allowed_methods = _operations_to_methods(
                    meta.get('detail_allowed_operations'))

            else:
                self.http_detail_allowed_methods = self.http_allowed_methods

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.list_allowed_operations = meta.get('list_allowed_operations')

        if self.list_allowed_operations is None:
            if meta.get('http_list_allowed_methods'):
                self.list_allowed_operations = _methods_to_operations(
                    meta.get('http_list_allowed_methods'))

            else:
                self.list_allowed_operations = self.allowed_operations

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.detail_allowed_operations = meta.get(
            'detail_allowed_operations')

        if self.detail_allowed_operations is None:
            if meta.get('http_detail_allowed_methods'):
                self.detail_allowed_operations = _methods_to_operations(
                    meta.get('http_detail_allowed_methods'))

            else:
                self.detail_allowed_operations = self.allowed_operations

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
