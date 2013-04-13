# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from .http import Request, Response
import bottle


class Resource(object):

    response = Response

    @classmethod
    def view(cls, *args, **kwargs):
        # Initiate the base view request cycle.
        path = kwargs.get('path', '')
        super(Resource, cls).view(Request(), path)

        # Return the response body.
        return bottle.response.body

    @classmethod
    def mount(cls, *args):
        # If the first argument is a string; then application was
        # not passed; use the default app, else use the first
        # argument as the application.
        if isinstance(args[0], six.string_types):
            app = bottle.app[-1]
            url = args[0]

        else:
            app = args[0]
            url = args[1]

        # Generate a name to use to mount this resource.
        name = '{}.{}'.format(cls.__module__, cls.__name__)
        name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # Apply the routing rules and add the URL routes
        # neccessary.
        rule = '{}{}<path:re:.*>'.format(url, cls.meta.name)
        app.route(rule, cls.meta.http_method_names, cls.view, name)
