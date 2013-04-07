# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
from flask import request
from .http import Request, Response


class Resource(object):
    """Specializes the RESTFul resource protocol for flask.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    #! Class to use to construct a response object.
    response = Response

    @classmethod
    def view(cls, *args, **kwargs):
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        path = re.sub(r'^/(.+)$', r'\1', kwargs.get('path', ''))
        if request.path.endswith('/'):
            path += '/'
        response = super(Resource, cls).view(Request(), path)

        # Facilitate the HTTP response and return it.
        return response.handle

    @classmethod
    def mount(cls, app, url, name=None):
        """
        Mounts the resource in the Flask container at the specified
        mount point.
        """
        # Generate a name to use to mount this resource.
        if name is None:
            name = '{}.{}'.format(cls.__module__, cls.__name__)
            name = '{}:{}:{}'.format('armet', name, cls.meta.name)

        # Mount this resource.
        methods = cls.meta.http_method_names
        rule = '{}{}'.format(url, cls.meta.name)
        app.add_url_rule(rule, name, cls.view, methods=methods)
        app.add_url_rule(
            rule + '/<path:path>', name + ':path', cls.view, methods=methods)
