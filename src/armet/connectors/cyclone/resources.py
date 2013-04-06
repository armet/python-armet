# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from .http import Request, Response
from armet import utils
from cyclone import web


class Handler(web.RequestHandler):
    """A cyclone request handler that forwards the request to armet. This
    involves overloading a few internal methods """

    def __init__(self, resource, *args, **kwargs):
        self.armet_resource = resource
        return super()

    def _execute_handler(self, r, args, kwargs):
        """We're overloading a private method here in oder to intercept the
        function execution and let armet handle it.
        """


class Resource(object):
    """Specializes the resource for cyclone.

    @note
        This is not what you derive from to create resources. Derive instead
        from `armet.resources.Resource`
    """

    #! Class to use to construct a response object
    response = Response

    # @classmethod
    # def redirect(cls, *args, **kwargs):
    #     pass

    # @classmethod
    # def view(cls, *args, **kwargss):
    #     pass

    # def asynchronous(self):
    #     """Makes this request asynchronous."""
    #     raise NotImplemented

    @classmethod
    def mount(cls, url, name=None):
        """Mounts this resource in the global bottle.py route database.
        """
        raise NotImplemented

    @utils.classproperty
    @utils.memoize_single
    def urls(cls):
        """Builds the url configuration for this resource, for use in an
        application object.
        """
        raise NotImplemented

    # @utils.classproperty
    @utils.memoize_single
    def handler(cls, *args, **kwargs):
        """Creates a thing?  This is the main entrypoint for the thing."""
        raise NotImplemented
