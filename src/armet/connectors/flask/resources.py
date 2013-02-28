# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet import utils, http
from armet.resources import base, meta
from flask import request, redirect
from werkzeug.wsgi import get_current_url


class Resource(base.Resource):
    """Specializes the RESTFul resource protocol for flask.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    @classmethod
    def redirect(cls, *args, **kwargs):
        env = request.environ
        env['PATH_INFO'] = super(Resource, cls).redirect(env['PATH_INFO'])
        return redirect(get_current_url(env), http.client.MOVED_PERMANENTLY)

    @classmethod
    def view(cls, *args, **kwargs):
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        response = super(Resource, cls).view(kwargs.get('path'))

        # Facilitate the HTTP response and return it.
        return response

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

        # Determine the appropriate methods.
        view = cls.view if cls.meta.trailing_slash else cls.redirect
        redirect = cls.redirect if cls.meta.trailing_slash else cls.view

        # Mount this resource.
        add = app.add_url_rule
        rule = '{}{}'.format(url, cls.meta.name)
        add(rule, name, redirect)
        add('{}/'.format(rule), '{}:trail'.format(name), view)
        add('{}<path:path>'.format(rule), '{}:path'.format(name), redirect)
        add('{}<path:path>/'.format(rule), '{}:path:trail'.format(name), view)
