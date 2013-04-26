# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.http import exceptions
from importlib import import_module
from . import http


class Resource(object):

    @classmethod
    @csrf.csrf_exempt
    def view(cls, django_request, *args, **kwargs):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        path = kwargs.get('path') or ''
        request = http.Request(django_request, path=path, asynchronous=async)
        response = http.Response(request, asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if response.asynchronous:
            # Defer the view to pass of control.
            view = super(Resource, cls).view
            import_module('gevent').spawn(view, request, response)

            # Construct the iterator and run the sequence once.
            iterator = iter(response._queue)
            content = next(iterator)

            def stream():
                # Yield our initial data.
                yield content

                # Iterate through the generator and yield its content
                # to the network stream.
                for chunk in iterator:
                    # Yield what we currently have in the buffer; if any.
                    yield chunk

            # Configure the streamer and return it
            response._handle.content = stream()
            return response._handle

        # Pass control off to the resource handler.
        result = super(Resource, cls).view(request, response)

        # If we got anything back; it is some kind of generator.
        if result is not None:
            # Construct the iterator and run the sequence once.
            iterator = iter(result)
            next(iterator)

            def stream():
                # Iterate through the generator and yield its content
                # to the network stream.
                for _ in iterator:
                    # Yield what we currently have in the buffer; if any.
                    yield response._stream.getvalue()

                    # Remove what we have in the buffer.
                    response._stream.truncate(0)
                    response._stream.seek(0)

            # Configure the streamer and return it
            response._handle.content = stream()
            return response._handle

        # Configure the response and return it.
        response._handle.content = response._stream.getvalue()
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
