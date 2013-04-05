# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from .http import Request, Response


class ResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! URL namespace to define the url configuration inside.
        self.url_name = meta.get('url_name')
        if not self.url_name:
            self.url_name = 'api_view'


class Resource(object):
    """Specializes the RESTFul abstract resource protocol for django.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    #! Class to use to construct a response object.
    response = Response

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


class ModelResource(object):
    """Specializes the RESTFul model resource protocol for django.

    @note
        This is not what you derive from to create resources. Import
        ModelResource from `armet.resources` and derive from that.
    """

    def read(self):
        # Serialize a simple queryset containing all models for now.
        from django.core import serializers
        queryset = self.meta.model.objects.all()
        return serializers.serialize('json', queryset)
