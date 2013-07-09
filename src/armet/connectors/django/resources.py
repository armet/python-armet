# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.http import exceptions
from . import http


class Resource(object):

    @classmethod
    @csrf.csrf_exempt
    def view(cls, django_request, *args, **kwargs):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        path = kwargs.get('path') or ''
        request = http.Request(django_request, path=path, asynchronous=async)
        response = http.Response(asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if async:
            # Defer the view to pass of control.
            import gevent
            gevent.spawn(super(cls.__base__, cls).view, request, response)

            # Construct and return the generator response.
            response._handle.content = cls.stream(response, response)
            return response._handle

        # Pass control off to the resource handler.
        result = super(cls.__base__, cls).view(request, response)

        # Configure the response and return it.
        response._handle.content = result
        return response._handle

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        return urls.patterns('', urls.url(
            r'^{}(?:$|(?P<path>[/:(.].*))'.format(cls.meta.name),
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
        return list(queryset.all())
