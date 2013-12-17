# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import bottle
from . import http


class Resource(object):

    @classmethod
    def view(cls, *args, **kwargs):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        request = http.Request(path=kwargs.get('path', ''), asynchronous=async)
        response = http.Response(asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if async:
            # Defer the view to pass of control.
            import gevent
            gevent.spawn(super(Resource, cls).view, request, response)

            # Construct and return a streamer.
            return cls.stream(response, response)

        # Pass control off to the resource handler.
        return super(Resource, cls).view(request, response)

    @classmethod
    def mount(cls, url='/', application=None):
        if application is None:
            # If no explicit application is passed; use
            # the current default application.
            application = bottle.app[-1]

        # Generate a name to use to mount this resource.
        name = '{}:{}:{}'.format('armet', cls.__module__, cls.meta.name)

        # Apply the routing rules and add the URL route.
        rule = '{}{}<path:re:$|(?:[/:(.].*)>'.format(url, cls.meta.name)
        application.route(rule, 'ANY', cls.view, name)
