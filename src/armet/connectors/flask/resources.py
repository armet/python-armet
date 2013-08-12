# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import flask
from werkzeug.routing import BaseConverter
from . import http
from armet import utils


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
        response = http.Response(asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if async:
            # Defer the view to pass of control.
            import gevent
            gevent.spawn(utils.super(Resource, cls).view, request, response)

            # Construct and return the generator response.
            response._handle.response = cls.stream(response, response)
            return response._handle

        # Pass control off to the resource handler.
        result = utils.super(Resource, cls).view(request, response)

        if isinstance(result, collections.Iterator):
            # Construct and return the generator response.
            response._handle.response = result
            return response._handle

        # Configure the response if we received any data.
        if result is not None:
            response._handle.data = result

        # Return the response.
        return response._handle

    @classmethod
    def mount(cls, url, app=None):
        # Generate a name to use to mount this resource.
        name = 'armet' + cls.__module__ + cls.meta.name + url

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
