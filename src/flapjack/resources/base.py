# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections.abc import Sequence
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls import patterns, url
import six
from .. import http, utils, authentication, exceptions


class Options(object):
    """
    """

    def __init__(self, cls, obj, bases):
        """
        """
        #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
        self.name = getattr(obj, 'name', cls.__name__.lower())

        #! List of understood HTTP methods.
        self.http_method_names = utils.config_fallback(getattr(obj,
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
        self.http_allowed_methods = getattr(obj, 'http_allowed_methods', (
                'get',
                'post',
                'put',
                'delete',
            ))

        #! List of allowed HTTP methods against a whole resource (eg /user).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_list_allowed_methods = getattr(obj,
            'http_list_allowed_methods', self.http_allowed_methods)

        #! List of allowed HTTP methods against a single resource (eg /user/1).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_detail_allowed_methods = getattr(obj,
            'http_detail_allowed_methods', self.http_allowed_methods)

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the differences
        #! between "PATCH and PUT", "PUT = create / update", etc.
        self.allowed_operations = getattr(obj, 'allowed_operations', (
                'read',
                'create',
                'update',
                'destroy',
            ))

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.list_allowed_operations = getattr(obj,
            'list_allowed_operations', self.allowed_operations)

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.detail_allowed_operations = getattr(obj,
            'detail_allowed_operations', self.allowed_operations)

        #! Authentication protocol to use to authenticate access to the
        #! resource.
        self.authentication = getattr(obj,
            'authentication', authentication.Authentication())

        # Ensure certain properties as iterables to ease algorithms
        for name in (
                    'http_allowed_methods',
                    'http_list_allowed_methods',
                    'http_detail_allowed_methods',
                    'allowed_operations',
                    'list_allowed_operations',
                    'detail_allowed_operations',
                    'authentication',
                ):
            value = getattr(self, name)
            if (not isinstance(value, six.string_types)
                    and isinstance(value, Sequence)):
                setattr(self, name, (value,))


class Meta(type):
    """
    """

    def __new__(cls, name, bases, attrs):
        """
        """
        # six.with_metaclass(..) adds an extra class called `NewBase` in the
        # inheritance tree: Resource > NewBase > object; ignore `NewBase`.
        parents = []
        for base in bases:
            if isinstance(base, Meta) and base.__name__ != 'NewBase':
                parents.append(base)

        if not parents or name == 'NewBase':
            # ignored type or not a subclass of `Resource`.
            return super(Meta, cls).__new__(cls, name, bases, attrs)

        # construct the class object.
        obj = super(Meta, cls).__new__(cls, name, bases, attrs)

        # instantiate the options; we aggregate all base classes constructed
        # option classes to allow the Options constructor to make use of
        # the base classes options to fill in for non-provided options.
        obj._meta = Options(obj, attrs,
            [x._meta for x in parents if hasattr(x, '_meta')])

        # return the constructed object; wipe off the magic -- not really.
        return obj


class Resource(six.with_metaclass(Meta)):
    """
    """

    @classmethod
    def url(cls, path=''):
        """Builds a url pattern using the passed `path` for this resource."""
        return url(
            r'^{}{}/??(?:\.(?P<fmt>[^/]*?))?/?$'.format(cls._meta.name, path),
            cls.view,
            name='api_view',
            kwargs={'resource': cls._meta.name},
        )

    @utils.classproperty
    @utils.memoize
    def urls(cls):
        """Builds the complete URL configuration for this resource."""
        return patterns('',
            cls.url(),
            cls.url(r'/(?P<id>[^/]?)'),
            cls.url(r'/(?P<id>[^/]?)/(?P<path>.*?)'),
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
            obj = resource(request)

            # Initiate the dispatch cycle
            data = obj.dispatch()

            # TODO: Build the response object
            # TODO: Apply pagination (?)
            # TODO: Return the response object
            return http.Response(str(data), status=http.OK)

        except exceptions.Error as ex:
            # Some known error was thrown; give an encoder to the exception
            # and encode an exception response.
            return ex.encode(None)

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

    def dispatch(self):
        """
        """
        # Assert authentication and attempt to get a valid user object.
        for auth in self._meta.authentication:
            user = auth.authenticate(self.request)
            if user is None:
                # A user object cannot be retrieved with this authn protocol.
                continue

            if user.is_authenticated() or auth.allow_anonymous:
                # A user object has been successfully retrieved.
                self.request.user = user
                break

        else:
            # A user was declared unauthenticated with some confidence.
            raise auth.Unauthenticated

        # TODO: Determine encoder
        # TODO: Determine decoder

        # Determine the HTTP method
        function = self._determine_method()

        # TODO: Assert resource-level authorization
        # TODO: Decode the request body (if non-empty)
        # TODO: Run clean cycle over decoded body (if non-empty body)
        # TODO: Assert object-level authorization (if non-empty body)

        # Delegate to the determined function.
        data = function()

        # Run prepare cycle over the returned data.
        # data = self.prepare(data)

        #
        return data

    @property
    def _allowed_methods(self):
        """Retrieves a list of allowed HTTP methods for the current request.
        """
        if self.identifier is not None:
            return self._meta.detail_allowed_methods

        else:
            return self._meta.list_allowed_methods

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

        if method not in self._meta.http_method_names:
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
