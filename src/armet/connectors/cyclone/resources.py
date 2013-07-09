# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from cyclone import web
# from cyclone import bottle
from twisted.internet import reactor
from . import http


class Handler(web.RequestHandler):
    """A cyclone request handler that forwards the request to armet.

    This involves overloading an internal method; `_execute_handler`.
    """

    def __init__(self, Resource, *args, **kwargs):
        # This must be set before we super, becuase that begins routing
        self.Resource = Resource

        # Pass off control to cyclone.
        super(Handler, self).__init__(*args, **kwargs)

    def __route(self, path):
        # Pass control off to the resource handler.
        self.Resource.view(self, path)

    def _execute_handler(self, _, args, kwargs):
        """
        This is copied directly from cyclone's repository with some
        minor changes to route all requests to a single method.

        For more information:
        https://github.com/fiorix/cyclone/blob/
        df43a89edd361d54f54e4d275ed5194512793789/cyclone/web.py#L1095-L1104
        """
        if not self._finished:
            # Decode arguments; changed slightly to use six (to be
            # python 3.x compliant).
            decode = self.decode_argument
            args = (decode(x) for x in args)
            kwargs = {k: decode(v, name=k) for k, v in six.iteritems(kwargs)}

            # Instead of calling each method, instead call the route handler
            deferred = self._deferred_handler(self.__route, *args, **kwargs)

            # Add callbacks; no changes here.
            deferred.addCallbacks(self._execute_success, self._execute_failure)
            self.notifyFinish().addCallback(self.on_connection_close)


class Resource(object):

    @classmethod
    def view(cls, handler, path):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        request = http.Request(handler, path=path or '', asynchronous=async)
        response = http.Response(handler, asynchronous=async)

        # Turn on asynchronous operation if we can.
        handler._auto_finish = not response.asynchronous

        # Pass control off to the resource handler.
        result = super(cls.__base__, cls).view(request, response)

        # If we got anything back; it is some kind of generator.
        if not response.asynchronous and result is not None:
            for _ in result:
                # Control was yielded to us and we're not async.. not much
                # we can do here.
                reactor.doIteration(0)

    @classmethod
    def mount(cls, url, application, host_pattern=r'.*'):
        # Add the handler normally.
        # NOTE: bottle-style routes are not supported at the moment.
        # <https://github.com/fiorix/cyclone/issues/108>
        application.add_handlers(host_pattern, (cls.rule(url),))

    @classmethod
    def rule(cls, url=r'^'):
        return (r'{}/{}(?:$|([/:(.].*))'.format(url, cls.meta.name),
                cls.handler)

    @classmethod
    def handler(cls, *args, **kwargs):
        return Handler(cls, *args, **kwargs)
