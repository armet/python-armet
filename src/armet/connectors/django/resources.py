# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.http import exceptions
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
        path = kwargs.get('path', '')
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
        # Initialize the queryset to the model manager.
        queryset = self.meta.model.objects

        if self.slug is not None:
            name = self.meta.slug.path.replace('.', '__')
            try:
                # Attempt to filter out and retrieve the specific
                # item referenced by the slug.
                return queryset.get(**{name: self.slug})

            except:
                # We found nothing; return Not Found - 404.
                raise exceptions.NotFound()

        # Return the entire queryset.
        return queryset.all()
