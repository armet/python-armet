# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.http import exceptions
from . import http


class Resource(object):

    @classmethod
    @csrf.csrf_exempt
    def view(cls, request, *args, **kwargs):
        # Construct request and response wrappers.
        request = http.Request(request, kwargs.get('path', ''))
        response = http.Response()

        # Pass control off to the resource handler.
        super(Resource, cls).view(request, response)

        # Return the response handle.
        return response.handle

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        return urls.patterns('', urls.url(
            r'^{}(?P<path>.*)'.format(cls.meta.name),
            cls.view,
            name='armet-api-{}'.format(cls.meta.name),
            kwargs={'resource': cls.meta.name}))


class ModelResource(object):

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
