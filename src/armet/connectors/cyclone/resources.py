# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from cyclone import web
from cyclone import bottle
from .http import Request, Response
from armet import http


class Handler(web.RequestHandler):
    """A cyclone request handler that forwards the request to armet. This
    involves overloading a few internal methods """

    def __init__(self, resource, *args, **kwargs):
        # This must be set before we super, becuase that begins routing
        self.resource = resource
        return super(Handler, self).__init__(*args, **kwargs)

    def route_request(self, path):
        self.resource.view(Request(self), path)

    def _execute_handler(self, r, args, kwargs):
        """We're overloading a private method here in oder to intercept the
        function execution and let armet handle it.
        """

        # This is copypasted directly from cyclone's repository with some
        # mior changes to route all requests to a specific method.
        # see for more information:
        # https://github.com/fiorix/cyclone/blob/
        # df43a89edd361d54f54e4d275ed5194512793789/cyclone/web.py#L1095-L1104
        if not self._finished:
            args = [self.decode_argument(arg) for arg in args]
            kwargs = dict((k, self.decode_argument(v, name=k))
                            for (k, v) in kwargs.iteritems())

            # Instead of calling each method, instead call the route handler
            d = self._deferred_handler(self.route_request, *args, **kwargs)

            d.addCallbacks(self._execute_success, self._execute_failure)
            self.notifyFinish().addCallback(self.on_connection_close)


class Resource(object):
    """Specializes the resource for cyclone.

    @note
        This is not what you derive from to create resources. Derive instead
        from `armet.resources.Resource`
    """

    #! Class to use to construct a response object
    def response(self, *args, **kwargs):
        return Response(self.request.handler, *args, **kwargs)

    @classmethod
    def mount(cls, url, application=None, host='.*'):
        """Mounts this resource in the specified application, or in the global
        bottle style application.
        """
        # assemble the routes that we're going to add to the handler
        routes = ((r'{}/{}(.*)'.format(url, cls.meta.name), cls.handler),)

        if application is None:
            # No application specified, add this to the bottle style handlers.
            # Note that this will die if the bottle app is run before these
            # routes are mounted... But then again, if that's what you're doing
            # then you're already in unknown territory.
            bottle._handlers.append(routes)

        else:
            # Add the handler
            application.add_handlers(host, routes)

    @classmethod
    def handler(cls, *args, **kwargs):
        """This is the main entrypoint for the resource."""
        return Handler(cls, *args, **kwargs)
