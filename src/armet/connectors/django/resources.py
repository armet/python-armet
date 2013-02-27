# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from django.http import HttpResponse
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.resources import base, meta, options


class ResourceOptions(options.ResourceOptions):
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
    def view(cls, request, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        response = super(Resource, cls).view(kwargs.get('path'))

        # Construct an HTTP response and return it.
        return HttpResponse(response)

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        # This is just declaring our mount point; slugs, parameters, etc.
        # are extracted later.
        kwargs = {'resource': cls.meta.name}
        return urls.patterns('',
            urls.url(r'^{}(?P<path>.*)/??'.format(cls.meta.name), cls.view,
                name=cls.meta.url_name, kwargs=kwargs),
            urls.url(r'^{}/??'.format(cls.meta.name), cls.view,
                name=cls.meta.url_name, kwargs=kwargs),
        )