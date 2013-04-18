# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import bottle
from . import http


class Resource(object):

    @classmethod
    def view(cls, *args, **kwargs):
        # Construct request and response wrappers.
        request = http.Request(kwargs.get('path', ''))
        response = http.Response()

        # Pass control off to the resource handler.
        super(Resource, cls).view(request, response)

        # Return the response body.
        return bottle.response.body

    @classmethod
    def mount(cls, url, application=None):
        # If no explicit application is passed; use
        # the current default application.
        application = bottle.app[-1]

        # Generate a name to use to mount this resource.
        name = '{}.{}'.format(cls.__module__, cls.__name__)
        name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # Apply the routing rules and add the URL route.
        rule = '{}{}<path:re:.*>'.format(url, cls.meta.name)
        application.route(rule, cls.meta.http_method_names, cls.view, name)
