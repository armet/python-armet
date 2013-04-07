# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
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
    def view(cls, request, *args, **kwargs):
        # Initiate the base view request cycle.
        path = re.sub(r'^/(.+)$', r'\1', kwargs.get('path', ''))
        response = super(Resource, cls).view(Request(request), path)

        # Construct an HTTP response and return it.
        return response.handle

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        url = urls.url(
            r'^{}(?P<path>.*)'.format(cls.meta.name),
            cls.view,
            name=cls.meta.url_name,
            kwargs={'resource': cls.meta.name})
        return urls.patterns('', url)


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
