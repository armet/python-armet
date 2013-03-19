# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet.resources import base, options, meta
from flask import request
from werkzeug.wsgi import get_current_url
from .http import Request, Response


class ResourceOptions(options.ResourceOptions):
    response = Response


class ResourceBase(meta.ResourceBase):
    options = ResourceOptions


class Resource(six.with_metaclass(ResourceBase, base.Resource)):
    """Specializes the RESTFul resource protocol for flask.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    @classmethod
    def redirect(cls, *args, **kwargs):
        env = request.environ
        res = super(Resource, cls).redirect(Request(), env['PATH_INFO'])
        env['PATH_INFO'] = res.header('Location')
        res.header('Location', get_current_url(env))
        return res.handle

    @classmethod
    def view(cls, *args, **kwargs):
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        response = super(Resource, cls).view(Request(), kwargs.get('path'))

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

        # Determine the appropriate methods.
        view = cls.view if cls.meta.trailing_slash else cls.redirect
        redirect = cls.redirect if cls.meta.trailing_slash else cls.view

        # Mount this resource.
        methods = cls.meta.http_method_names
        add = lambda *args: app.add_url_rule(*args, methods=methods)
        rule = '{}{}'.format(url, cls.meta.name)
        add(rule, name, redirect)
        add('{}/'.format(rule), '{}:trail'.format(name), view)
        add('{}<path:path>'.format(rule), '{}:path'.format(name), redirect)
        add('{}<path:path>/'.format(rule), '{}:path:trail'.format(name), view)
