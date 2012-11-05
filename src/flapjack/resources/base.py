# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls import patterns, url
import six
from .. import http, utils, authentication


class Options(object):
    """
    """

    def _override(self, name, default=None):
        """
        """
        if hasattr(self._meta, name):
            # configuration property was found on the `Meta` of the
            # current resource.
            return getattr(self._meta, name)

        for base in self._bases:
            if hasattr(base, name):
                # configuration property was found somewhere on a base
                # class.
                return getattr(base, name)

        # configuration property was never found; return the default.
        return default

    def __init__(self, cls, meta, bases):
        """
        """
        #! Meta configuration class.
        self._meta = meta

        #! Meta configuration class objects for bases classes.
        self._bases = bases if bases else []

        #! List of understood HTTP methods.
        self.http_method_names = self._override('http_method_names', (
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
        self.http_allowed_methods = self._override('http_allowed_methods', (
            'get',
            'post',
            'put',
            'delete',
        ))

        #! List of allowed HTTP methods against a whole resource (eg /user).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_list_allowed_methods = self._override(
            'http_list_allowed_methods', self.http_allowed_methods)

        #! List of allowed HTTP methods against a single resource (eg /user/1).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_detail_allowed_methods = self._override(
            'http_detail_allowed_methods', self.http_allowed_methods)

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the differences
        #! between "PATCH and PUT", "PUT = create / update", etc.
        self.allowed_operations = self._override('allowed_operations', (
            'read',
            'create',
            'update',
            'destroy',
        ))

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.list_allowed_operations = self._override(
            'list_allowed_operations', self.allowed_operations)

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.detail_allowed_operations = self._override(
            'detail_allowed_operations', self.allowed_operations)

        #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
        self.name = self._override('name', cls.__name__.lower())

        #! Authentication protocol to use to authenticate access to the
        #! resource.
        self.authentication = self._override('authentication',
            (authentication.Authentication(),))


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
        obj._meta = Options(obj, attrs.get('Meta'),
            [x._meta for x in parents if hasattr(x, '_meta')])

        # return the constructed object; wipe off the magic -- not really.
        return obj


class Resource(six.with_metaclass(Meta)):
    """
    """

    class Meta:
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
        return patterns(
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
            segments = kwargs.get('path').split('/')
            segments = [x for x in segments if x]
            cls.traverse(segments)
            # TODO: Instantiate the resource
            # TODO: Initiate the dispatch
            # TODO: Build the response object
            # TODO: Apply pagination (?)
            # TODO: Return the response object
            return http.Response(status=http.OK)

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

    def dispatch(self):
        """
        """
        # Assert authentication and attempt to get a valid user object.
        for authentication in self._meta.authentication:
            user = authentication.authenticate(self.request)
            if user is not None:
                # A user object has been successfully retrieved.
                self.request.user = user
                break

        else:
            # A user was never retreived; return that we have failed
            # to authenticate ourselves.
            return authentication.unauthenticated

        # TODO: Determine encoder
        # TODO: Determine decoder
        # TODO: Determine the HTTP method
        # TODO: Determine the resource operation
        # TODO: Assert resource-level authorization
        # TODO: Decode the request body (if non-empty)
        # TODO: Run clean cycle over decoded body (if non-empty body)
        # TODO: Assert object-level authorization (if non-empty body)
        return None
