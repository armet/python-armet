# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import bottle
from . import http
from importlib import import_module


class Resource(object):

    @classmethod
    def view(cls, *args, **kwargs):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        request = http.Request(path=kwargs.get('path', ''), asynchronous=async)
        response = http.Response(asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if response.asynchronous:
            # Defer the view to pass of control.
            view = super(Resource, cls).view
            import_module('gevent').spawn(view, request, response)

            def stream():
                # Construct the iterator and run the sequence once.
                iterator = iter(response._queue)
                chunk = next(iterator)

                # Push the initial HTTP response.
                response._push()

                if chunk:
                    # Yield our initial data (if any).
                    yield chunk

                # Iterate through the asynchronous queue.
                for chunk in iterator:
                    if chunk:
                        # Yield the pushed chunk to bottle.
                        yield chunk

            # Return our asynchronous streamer.
            return stream()

        # Pass control off to the resource handler.
        result = super(Resource, cls).view(request, response)

        # If we got anything back; it is some kind of generator.
        if result is not None:
            # Construct the iterator and run the sequence once.
            iterator = iter(result)
            next(iterator)

            # Push the initial HTTP response.
            response._push()

            def stream():
                # Iterate through the generator and yield its content
                # to the network stream.
                for _ in result:
                    if response._stream.tell():
                        # Yield what we currently have in the buffer; if any.
                        yield response._stream.getvalue()

                        # Remove what we have in the buffer.
                        response._stream.truncate(0)
                        response._stream.seek(0)

            # Return our streamer.
            return stream()

        # Push the initial HTTP response.
        response._push()

        # Return the one 'chunk' of data.
        return response._stream.getvalue()

    @classmethod
    def mount(cls, url='/', application=None):
        # If no explicit application is passed; use
        # the current default application.
        application = bottle.app[-1]

        # Generate a name to use to mount this resource.
        name = '{}.{}'.format(cls.__module__, cls.__name__)
        name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # Apply the routing rules and add the URL route.
        pattern = r'$|(?:[/:(.].*)'
        rule = '{}{}<path:re:{}>'.format(url, cls.meta.name, pattern)
        application.route(rule, cls.meta.http_method_names, cls.view, name)
