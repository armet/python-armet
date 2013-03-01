# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from django.http import HttpResponse
from django.conf import urls
from django.views.decorators import csrf
from armet import utils, resources
from armet.resources import base, meta, options


class Request(resources.Request):
    """Implements the RESTFul request abstraction for django.
    """

    def __init__(self, request):
        self.handle = request

    @property
    @utils.memoize_single
    def method(self):
        override = self['X-Http-Method-Override']
        return override.upper() if override else self.handle.method

    @utils.memoize
    def __getitem__(self, name):
        name = name.replace('-', '_').upper()
        if name != 'CONTENT_TYPE':
            name = 'HTTP_{}'.format(name)
        return self.handle.META.get(name)


class Response(resources.Response):
    """Implements the RESTFul response abstraction for django.
    """

    def __init__(self, *args, **kwargs):
        self.handle = HttpResponse()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self.handle.status_code

    @status.setter
    def status(self, value):
        self.handle.status_code = value

    def __getitem__(self, name):
        return self.handle.get(name)

    def __setitem__(self, name, value):
        self.handle[name] = value


class ResourceOptions(options.ResourceOptions):
    response = Response

    def __init__(self, options, name, bases):
        super(ResourceOptions, self).__init__(options, name, bases)
        #! URL namespace to define the url configuration inside.
        self.url_name = options.get('url_name')
        if not self.url_name:
            self.url_name = 'api_view'


class ResourceBase(meta.ResourceBase):
    options = ResourceOptions


class Resource(six.with_metaclass(ResourceBase, base.Resource)):
    """Specializes the RESTFul resource protocol for django.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    @classmethod
    @csrf.csrf_exempt
    def redirect(cls, request, *args, **kwargs):
        res = super(Resource, cls).redirect(Request(request), request.path)
        request.path = res.handle['Location']
        res.handle['Location'] = request.get_full_path()
        return res.handle

    @classmethod
    @csrf.csrf_exempt
    def view(cls, request, *args, **kwargs):
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        response = super(Resource, cls).view(
            Request(request), kwargs.get('path'))

        # Construct an HTTP response and return it.
        return response.handle

    @utils.classproperty
    @utils.memoize_single
    def urls(cls):
        """Builds the URL configuration for this resource."""
        view = cls.view if cls.meta.trailing_slash else cls.redirect
        redirect = cls.redirect if cls.meta.trailing_slash else cls.view
        url = lambda path, method: urls.url(
            path.format(cls.meta.name),
            method,
            name=cls.meta.url_name,
            kwargs={'resource': cls.meta.name})
        return urls.patterns(
            '',
            url(r'^{}(?P<path>.*)/', view),
            url(r'^{}(?P<path>.*)', redirect),
            url(r'^{}/', view),
            url(r'^{}', redirect))
