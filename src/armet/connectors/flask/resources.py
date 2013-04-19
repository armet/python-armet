# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import flask
from werkzeug.routing import BaseConverter
from . import http


class RegexConverter(BaseConverter):
    """Regular expression URL converter for werkzeug / flask.
    """

    def __init__(self, url_map, pattern='(.*)'):
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
        request = http.Request(path)
        response = http.Response()

        # Pass control off to the resource handler.
        super(Resource, cls).view(request, response)

        # Return the response handle.
        return response._handle

    @classmethod
    def mount(cls, url, app):
        # Generate a name to use to mount this resource.
        name = '{}.{}'.format(cls.__module__, cls.__name__)
        name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # Prepare the flask application to accept armet resources.
        # The strict slashes setting must be False for our routes.
        strict_slashes = app.url_map.strict_slashes = False

        # Ensure that there is a compliant regex converter available.
        converter = app.url_map.converters['default']
        app.url_map.converters['default'] = RegexConverter

        # Mount this resource.
        methods = cls.meta.http_method_names
        rule = '{}{}<path>'.format(url, cls.meta.name)
        app.add_url_rule(rule, name, cls.view, methods=methods)

        # Restore the flask environment.
        app.url_map.strict_slashes = strict_slashes
        app.url_map.converters['default'] = converter
