# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from django.http import HttpResponse
from django.conf import urls
from armet import utils
from armet.resources import base


class ResourceBase(base.ResourceBase):
    pass


class Resource(six.with_metaclass(ResourceBase, base.Resource)):
    """Specializes the RESTFul resource protocol for django.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    #! URL namespace to define the url configuration inside.
    url_name = 'api_view'

    @classmethod
    def view(cls, request, *args, **kwargs):
       return HttpResponse(cls().dispatch())

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        # This is just declaring our mount point; slugs, parameters, etc.
        # are extracted later.
        pattern = '^{}/??(?P<path>.*)/??'.format(cls.name)
        return urls.patterns('', urls.url(pattern, cls.view,
            name=cls.url_name))
