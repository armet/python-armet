# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import flask
from werkzeug.routing import BaseConverter
from . import http
from importlib import import_module


class RegexConverter(BaseConverter):
    """Regular expression URL converter for werkzeug / flask.
    """

    def __init__(self, url_map, pattern=r'(.*)'):
        super(RegexConverter, self).__init__(url_map)
        self.regex = pattern


class Resource(object):

    @classmethod
    def view(cls, *args, **kwargs):
        # Initiate the base view request cycle.
        path = kwargs.get('path', '')
        if flask.request.path.endswith('/'):
            # The trailing slash is stripped for fun by werkzeug.
            path += '/'

        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        request = http.Request(path=path, asynchronous=async)
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
            response._handle.response = stream()
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
                for chunk in iterator:
                    # Yield what we currently have in the buffer; if any.
                    yield response._stream.getvalue()

                    # Remove what we have in the buffer.
                    response._stream.truncate(0)
                    response._stream.seek(0)

            # Configure the streamer and return it
            response._handle.response = stream()
            return response._handle

        # Configure the response and return it.
        response._handle.data = response._stream.getvalue()
        return response._handle

    @classmethod
    def mount(cls, url, app=None):
        # Generate a name to use to mount this resource.
        name = '{}.{}'.format(cls.__module__, cls.__name__)
        name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # If application is not provided; make use of the app context.
        if app is None:
            app = flask.current_app

        # Prepare the flask application to accept armet resources.
        # The strict slashes setting must be False for our routes.
        strict_slashes = app.url_map.strict_slashes = False

        # Ensure that there is a compliant regex converter available.
        converter = app.url_map.converters['default']
        app.url_map.converters['default'] = RegexConverter

        # Mount this resource.
        pattern = '{}{}<path>'.format(url, cls.meta.name)
        rule = app.url_rule_class(pattern, endpoint=name)
        app.url_map.add(rule)
        app.view_functions[name] = cls.view

        # Restore the flask environment.
        app.url_map.strict_slashes = strict_slashes
        app.url_map.converters['default'] = converter
