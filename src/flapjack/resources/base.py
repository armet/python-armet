# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls import patterns, url
import six
from .. import http, utils, exceptions


class Meta(type):
    """
    """

    def __new__(cls, name, bases, attrs):
        """
        """
        # construct the class object.
        obj = super(Meta, cls).__new__(cls, name, bases, attrs)

        #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
        obj.name = getattr(obj, 'name', obj.__name__.lower())

        #! List of understood HTTP methods.
        obj.http_method_names = utils.config_fallback(getattr(obj,
            'http_method_names', None), 'http.methods', (
                'get',
                'post',
                'put',
                'delete',
                'patch',
                'options',
                'head',
                'connect',
                'trace',
            ))

        #! List of allowed HTTP methods.
        obj.http_allowed_methods = getattr(obj, 'http_allowed_methods', (
                'get',
                'post',
                'put',
                'delete',
            ))

        #! List of allowed HTTP methods against a whole resource (eg /user).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        obj.http_list_allowed_methods = getattr(obj,
            'http_list_allowed_methods', obj.http_allowed_methods)

        #! List of allowed HTTP methods against a single resource (eg /user/1).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        obj.http_detail_allowed_methods = getattr(obj,
            'http_detail_allowed_methods', obj.http_allowed_methods)

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the differences
        #! between "PATCH and PUT", "PUT = create / update", etc.
        obj.allowed_operations = getattr(obj, 'allowed_operations', (
                'read',
                'create',
                'update',
                'destroy',
            ))

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        obj.list_allowed_operations = getattr(obj,
            'list_allowed_operations', obj.allowed_operations)

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        obj.detail_allowed_operations = getattr(obj,
            'detail_allowed_operations', obj.allowed_operations)

        #! Mapping of encoders known by this resource.
        obj.encoders = utils.config_fallback(getattr(obj, 'encoders', None),
            'encoders', {
                    'json': 'flapjack.encoders.Json'
                })

        #! List of allowed encoders of the understood encoders.
        obj.allowed_encoders = getattr(obj, 'allowed_encoders', (
                'json',
            ))

        #! List of allowed encoders of the understood encoders.
        obj.default_encoder = utils.config_fallback(getattr(obj,
            'default_encoder', None), 'default.encoder',
            obj.encoders.keys()[0])

        #! Authentication protocol to use to authenticate access to the
        #! resource.
        obj.authentication = utils.config_fallback(
            getattr(obj, 'authentication', None), 'resource.authentication', (
                    'flapjack.authentication.Authentication',
                ))

        for_all = utils.for_all
        test = lambda x: isinstance(x, six.string_types)
        method = lambda x: x()
        for name in (
                    'encoders',
                    'authentication',
                ):
            # Ensure certain properties that may be name qualified instead of
            # class objects are resolved to be class objects.
            setattr(obj, name, for_all(getattr(obj, name), utils.load, test))

            # Ensure things that need to be instantied are instantiated
            setattr(obj, name, for_all(getattr(obj, name), method, callable))

        # return the constructed object; wipe off the magic -- not really.
        return obj


class Resource(six.with_metaclass(Meta)):
    """
    """

    @classmethod
    def url(cls, path=''):
        """Builds a url pattern using the passed `path` for this resource."""
        return url(
            r'^{}{}/??(?:\.(?P<format>[^/]*?))?/?$'.format(cls.name, path),
            cls.view,
            name='api_view',
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
            obj = resource(request,
                identifier=kwargs.get('identifier'),
                format=kwargs.get('format'))

            # Initiate the dispatch cycle and return its result
            return obj.dispatch()

        except exceptions.Error as ex:
            # Some known error was thrown before the dispatch cycle; dispatch.
            return ex.dispatch()

        except BaseException:
            if settings.DEBUG:
                # TODO: Something went wrong; return the encoded error message.
                # For now; re-raise the erorr.
                raise

            # TODO: Notify system administrator of error
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

        #! Encoder that is used for the cycle of the request.
        self._encoder = None

    def dispatch(self):
        """
        """
        try:
            # Assert authentication and attempt to get a valid user object.
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

            # Determine the HTTP method
            function = self._determine_method()

            # Detect an appropriate encoder.
            self._determine_encoder()

            # TODO: Assert resource-level authorization

            if self.request.body is not None:
                # TODO: Determine decoder
                # TODO: Decode the request body (if non-empty)
                # TODO: Run clean cycle over decoded body (if non-empty body)
                # TODO: Assert object-level authorization (if non-empty body)
                pass

            # Delegate to the determined function.
            data, status = function()

            # Run prepare cycle over the returned data.
            data = self.prepare(data)

            # Build and return the response object
            return self.process(data, status)

        except exceptions.Error as ex:
            # Known error occured; encode it and return the response.
            return ex.dispatch(self._encoder)

    def process(self, data, status):
        """Builds a response object from the data and status code."""
        response = http.Response(status=status)
        if data is not None:
            response.content = self._encoder.encode(data)
            response['Content-Type'] = self._encoder.mimetype

        return response

    def prepare(self, data):
        """Prepares the data for transmission."""
        # TODO: Do something here
        return data

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
                self._encoder = self.encoders.get(name)
                if self._encoder is not None:
                    # Found an appropriate encoder; we're done
                    return

        elif accept is not None and accept.strip() != '*/*':
            for name in self.allowed_encoders:
                encoder = self.encoders[name]
                if encoder.can_transcode(self.request.META['HTTP_ACCEPT']):
                    # Found an appropriate encoder; we're done
                    self._encoder = encoder
                    return

        else:
            # Neither `.fmt` nor an accept header was specified
            self._encoder = self.encoders.get(self.default_encoder)
            print(self.default_encoder)
            return

        # Failed to find an appropriate encoder
        # Get dictionary of available formats
        available = {}
        for name in self.allowed_encoders:
            available[name] = self.encoders[name].mimetype

        # Encode the response using the appropriate exception
        raise exceptions.NotAcceptable(available)

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
            data['message'] = ('Operation not allowed on `{}`; '
                'see `allowed` for allowed operations.').format(operation)

            raise exceptions.Forbidden(data)
