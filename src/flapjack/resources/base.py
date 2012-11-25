# -*- coding: utf-8 -*-
"""Defines a RESTful resource access protocol.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
from collections import Mapping
import logging
import six
from six import string_types
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from .. import utils, http, exceptions


# Get an instance of the logger.
logger = logging.getLogger('flapjack.resources')


class BaseResource(object):
    """Defines a RESTful resource access protocol for generic resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `flapjack.resources.Resource` (defined in
        the `__init__.py`).
    """

    #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
    name = None

    #! Form class to serve as the recipient of data from the client.
    form = None

    #! List of understood HTTP methods.
    http_method_names = (
        'get',
        'post',
        'put',
        'delete',
        'patch',
        'options',
        'head',
        'connect',
        'trace',
    )

    #! List of allowed HTTP methods.
    http_allowed_methods = (
        'get',
        'post',
        'put',
        'delete',
    )

    #! List of allowed HTTP methods against a whole
    #! resource (eg /user); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_list_allowed_methods = None

    #! List of allowed HTTP methods against a single
    #! resource (eg /user/1); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_detail_allowed_methods = None

    #! List of allowed operations.
    #! Resource operations are meant to generalize and blur the
    #! differences between "PATCH and PUT", "PUT = create / update",
    #! etc.
    allowed_operations = (
        'read',
        'create',
        'update',
        'destroy',
    )

    #! List of allowed operations against a whole resource.
    #! If undeclared or None, will be defaulted to
    #! `allowed_operations`.
    list_allowed_operations = None

    #! List of allowed operations against a single resource.
    #! If undeclared or None, will be defaulted to `allowed_operations`.
    detail_allowed_operations = None

    #! Mapping of encoders known by this resource.
    encoders = {
        'json': 'flapjack.encoders.Json',
    }

    #! List of allowed encoders of the understood encoders.
    allowed_encoders = (
        'json',
    )

    #! Name of the default encoder of the list of understood encoders.
    default_encoder = 'json'

    #! List of decoders known by this resource.
    decoders = (
        'flapjack.decoders.Form',
    )

    #! URL namespace to define the url configuration inside.
    url_name = 'api_view'

    #! Blacklist of fields to exclude from display.
    exclude = None

    #! Whitelist of fields to include in the display.
    fields = None

    #! Additional fields to include in the display.
    include = None

    #! Whitelist of fields that are filterable.
    #! Default is to be an empty () which excludes all fields from filtering.
    #! To have all fields be eligible for filtering, explicitly specify
    #! `filterable = None` on a resource or any of its parents.
    filterable = None

    #! The name of the resource URI field on the resource.
    #! Specify `None` to not have the URI be included.
    resource_uri = 'resource_uri'

    #! Authentication protocol(s) to use to authenticate access to
    #! the resource.
    authentication = ('flapjack.authentication.Authentication',)

    @classmethod
    def slug(cls, obj):
        """
        The resource URI segment which is used to access and identify this
        resource.

        @note
            This method is only valid and used if this resource is exposed
            via an urls.py.

        @example
            The following would generate a resource URI (assuming a resource
            name of `MyResource` and a mount of `api`): `/api/MyResource/<pk>`
            @code
                # Use the attribute named 'pk' as the resource URI (default for
                # model resources).
                return obj.pk
        """
        pass

    @classmethod
    def url(cls, path=''):
        """Builds a url pattern using the passed `path` for this resource."""
        return url(
            r'^{}{}/??(?:\.(?P<format>[^/]*?))?/?$'.format(cls.name, path),
            cls.view,
            name=cls.url_name,
            kwargs={'resource': cls.name},
        )

    @utils.classproperty
    @utils.memoize
    def urls(cls):
        """Builds the complete URL configuration for this resource."""
        return patterns('',
            cls.url(),
            cls.url(r'/(?P<identifier>[^/]+?)'),
            cls.url(r'/(?P<identifier>[^/]+?)/(?P<path>.*?)'),
        )

    @classmethod
    @csrf_exempt
    def view(cls, request, *args, **kwargs):
        """
        Entry-point of the request cycle; handles resource creation and
        delegation.
        """
        try:
            # Traverse path segments; determine final resource
            segments = kwargs.get('path', '').split('/')
            segments = [x for x in segments if x]
            resource = cls.traverse(segments)

            # Instantiate the resource
            obj = resource(
                request,
                identifier=kwargs.get('identifier'),
                format=kwargs.get('format'))

            # Initiate the dispatch cycle and return its result
            return obj.dispatch()

        except exceptions.Error as ex:
            # Some known error was thrown before the dispatch cycle; dispatch.
            return ex.dispatch()

        except BaseException:
            # TODO: Notify system administrator of error

            # Log that an unknown exception occured to help those poor
            # system administrators.
            logger.exception('Internal server error.')

            # Return an empty body indicative of a server failure.
            return http.Response(status=http.INTERNAL_SERVER_ERROR)

    @classmethod
    def traverse(cls, segments):
        """
        """
        if not segments:
            # No sub-resource path provided; return our cls
            return cls

    def __init__(self, request, **kwargs):
        """
        """
        #! Django WSGI request object.
        self.request = request

        #! Identifier of the resource if we are being accessed directly.
        self.identifier = kwargs.get('identifier')

        #! Explicitly declared format of the request.
        self.format = kwargs.get('format')

        #! Path of the resource.
        self.path = kwargs.get('path')

    def dispatch(self):
        """
        """
        # Set some defaults so we can reference this later
        encoder = None
        try:
            # Assert authentication and attempt to get a valid user object.
            self.authenticate()

            # Determine the HTTP method
            function = self._determine_method()

            # Detect an appropriate encoder.
            encoder = self._determine_encoder()

            # TODO: Assert resource-level authorization

            if self.request.body:
                # Determine an approparite decoder.
                decoder = self._determine_decoder()

                # Decode the request body
                content = decoder.decode(self.request, self._fields)

                # Run clean cycle over decoded body
                content = self.clean(content)

                # TODO: Assert object-level authorization

            # Delegate to the determined function.
            data, status = function()

            # Run prepare cycle over the returned data.
            data = self.prepare(data)

            # Build and return the response object
            return self.process(encoder, data, status)

        except exceptions.Error as ex:
            # Known error occured; encode it and return the response.
            return ex.dispatch(encoder)

    def authenticate(self):
        """Attempts to assert authentication."""
        for auth in self.authentication:
            user = auth.authenticate(self.request)
            if user is None:
                # A user object cannot be retrieved with this
                # authn protocol.
                continue

            if user.is_authenticated() or auth.allow_anonymous:
                # A user object has been successfully retrieved.
                self.request.user = user
                break

        else:
            # A user was declared unauthenticated with some confidence.
            raise auth.Unauthenticated

    def process(self, encoder, data, status):
        """Builds a response object from the data and status code."""
        response = http.Response(status=status)
        if data is not None:
            response.content = encoder.encode(data)
            response['Content-Type'] = encoder.mimetype

        return response

    def prepare(self, data):
        """Prepares the data for transmission."""
        prepare = self.item_prepare
        if not (isinstance(data, string_types) or isinstance(data, Mapping)):
            try:
                # Attempt to prepare each item of the iterable (as long as
                # we're not a string or some sort of mapping).
                return (prepare(x) for x in data)

            except TypeError as ex:
                # Definitely not an iterable.
                logger.debug(ex, exc_info=True)

        # Prepare just the singular value and return it.
        return prepare(data)

    def item_prepare(self, item):
        """Prepares an item for transmission."""
        # Initialize the object that will hold the item.
        obj = {}

        # Set the resource uri on the object.
        if self.resource_uri is not None:
            obj[self.resource_uri] = self.reverse(item)

        # Iterate through the fields and build the object from the item.
        for name, field in six.iteritems(self._fields):
            if field.visible:
                # Prepare field and set on the object.
                try:
                    obj[name] = field.prepare(self, item, field.accessor(item))

                except TypeError:
                    # No accessor provided; carry on.
                    obj[name] = field.prepare(self, item, None)

        if not self.path:
            # No need to navigate the object; return what we've constructed.
            return obj

        # Navigate through some hoops to return from what we construct.
        for segment in self.path.split('__'):
            try:
                # Attempt to garner access into the object
                # TODO: Optimize object access here
                try:
                    # This is likely still a dictionary
                    obj = obj[segment]

                except KeyError:
                    # Well; here goes nothing
                    obj = getattr(obj, segment)

            except AttributeError as ex:
                # Denied; ouch
                logger.debug(ex, exc_info=True)

                # We are not part of the URL here so we return `None` to
                # represent that we could not find an object.
                return None

        # Just return the object.
        return obj

    def clean(self, data):
        """Cleans data from the request for processing."""
        # TODO: Resolve relation URIs (eg. /resource/:slug/).
        # TODO: Run micro-clean cycle using field-level cleaning in order to
        #       support things like fuzzy dates.

        if self.form is not None:
            # Instantiate form using provided data (if form exists).
            # form = self.form()
            pass

        return data

    #! Identifier to access the resource URL as a whole.
    _URL = 2

    #! Identifier to access the resource individualy.
    _URL_IDENTIFIER = 1

    @classmethod
    @utils.memoize
    def _url_format(cls, identifier):
        """Gets the string format for a URL for this resource."""
        # HACK: This is a hackish way to get a string format representing
        #       the URL that would have been reversed with `reverse`. Speed
        #       increases of ~192%. Proper way would be a django internal
        #       function to just do the url reversing `halfway` but we'll
        #       see if that can make it in.
        # TODO: Perhaps move this and the url reverse speed up bits out ?
        urlmap = cls._resolver.reverse_dict.getlist(cls.view)[identifier][0][0]
        url = urlmap[0]
        for param in urlmap[1]:
            url = url.replace('({})'.format(param), '')
        return '{}{}'.format(cls._prefix, url)

    @classmethod
    def reverse(cls, value=None):
        """Reverses a URL for the resource or for the passed object."""
        # Not using `iri_to_uri` here; therefore only ASCII is permitted.
        if value is not None:
            return cls._url_format(
                cls._URL_IDENTIFIER) % cls.slug(value)

        return cls._url_format(cls._URL)

    # TODO: def resolve(self):

    def get(self):
        """Processes a `GET` request.

        @returns
            A tuple containing the data and response status sequentially.
        """
        # Ensure we're allowed to perform this operation.
        self._assert_operation('read')

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.identifier is not None:
            if not items:
                # Requested a specific resource but no resource was returned.
                raise exceptions.NotFound()

            if (not isinstance(items, six.string_types)
                    and not isinstance(items, collections.Mapping)):
                # Ensure we return only a single object if we were requested
                # to return such.
                items = items[0]

        else:
            if items is None:
                # Ensure we at least have an empty list
                items = []

        # Return the response
        return items, http.OK

    def post(self):
        # Return the response
        return None, http.NO_CONTENT

    @property
    def _allowed_methods(self):
        """Retrieves a list of allowed HTTP methods for the current request.
        """
        if self.identifier is not None:
            return self.http_detail_allowed_methods

        return self.http_list_allowed_methods

    def _determine_method(self):
        """Determine the actual HTTP method being used and if it is acceptable.
        """
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in self.request.META:
            # Someone is using a client that isn't smart enough to send proper
            # verbs; but can still send headers.
            method = self.request.META['HTTP_X_HTTP_METHOD_OVERRIDE'].lower()
            self.request.method = method.upper()

        else:
            # Halfway intelligent client; proceed as normal.
            method = self.request.method.lower()

        if method not in self.http_method_names:
            # Method not understood by our library; die.
            raise exceptions.NotImplemented()

        if method not in self._allowed_methods:
            # Method is not in the list of allowed HTTP methods for this
            # access of the resource.
            allowed = (m.upper() for m in self._allowed_methods)
            raise exceptions.MethodNotAllowed(', '.join(allowed).strip())

        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Method understood and allowed but not implemented; stupid us.
            raise exceptions.NotImplemented()

        # Method is just fine; toss 'er back
        return function

    def _determine_encoder(self):
        """Determine the encoder to use according to the request object.
        """
        accept = self.request.META['HTTP_ACCEPT']
        if self.format is not None:
            # An explicit form was supplied; attempt to get it directly
            name = self.format.lower()
            if name in self.allowed_encoders:
                encoder = self.encoders.get(name)
                if encoder is not None:
                    # Found an appropriate encoder; we're done
                    return encoder

        elif accept is not None and accept.strip() != '*/*':
            for name in self.allowed_encoders:
                encoder = self.encoders[name]
                if encoder.can_transcode(self.request.META['HTTP_ACCEPT']):
                    # Found an appropriate encoder; we're done
                    return encoder

        else:
            # Neither `.fmt` nor an accept header was specified
            return self.encoders.get(self.default_encoder)

        # Failed to find an appropriate encoder
        # Get dictionary of available formats
        available = {}
        for name in self.allowed_encoders:
            available[name] = self.encoders[name].mimetype

        # Encode the response using the appropriate exception
        raise exceptions.NotAcceptable(available)

    def _determine_decoder(self):
        """Determine the decoder to use according to the request object.
        """
        # Attempt to get the content-type; default to an appropriate value.
        content = self.request.META.get(
            'CONTENT_TYPE', 'application/octet-stream')

        # Attempt to find a decoder and on failure, die.
        for decoder in self.decoders:
            if decoder.can_transcode(content):
                # Good; return the decoder
                return decoder

        # Failed to find an appropriate decoder; we have no idea how to
        # handle the data.
        raise exceptions.UnsupportedMediaType()

    @property
    def _allowed_operations(self):
        """Retrieves a list of allowed operations for the current request.
        """
        if self.identifier is not None:
            return self.detail_allowed_operations

        return self.list_allowed_operations

    def _assert_operation(self, operation):
        """Determine of the requested operation is allowed in this context.
        """
        if operation not in self._allowed_operations:
            # Operation not allowed in this context; bail
            data = {}
            data['allowed'] = self._allowed_operations
            data['message'] = (
                'Operation not allowed on `{}`; '
                'see `allowed` for allowed operations.').format(operation)

            raise exceptions.Forbidden(data)
