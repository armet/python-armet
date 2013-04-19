# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import bottle
from . import http


class Resource(object):

    @classmethod
    def view(cls, *args, **kwargs):
        # Construct request and response wrappers.
        request = http.Request(kwargs.get('path', ''))
        response = http.Response(asynchronous=cls.meta.asynchronous)

        # Defer the execution thread if we're running asynchronously.
        if cls.meta.asynchronous:
            def view():
                # Pass control off to the resource handler.
                super(Resource, cls).view(request, response)

            # Defer the view.
            import gevent
            gevent.spawn(view)
            return response._queue

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
                for chunk in result:
                    # Yield what we currently have in the buffer; if any.
                    yield response._stream.getvalue()

                    # Remove what we have in the buffer.
                    response._stream.truncate(0)

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
        rule = '{}{}<path:re:.*>'.format(url, cls.meta.name)
        application.route(rule, cls.meta.http_method_names, cls.view, name)
