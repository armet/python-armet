# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from cyclone import web
from twisted.internet import reactor, threads
from threading import Thread
from .utils import force_import_module


_reactor_thread = None


def start_reactor(*args, **kwargs):
    """
    Start the Twisted reactor in a separate thread so that it can
    run alongside the tests.
    """
    global _reactor_thread

    def start(*args, **kwargs):
        reactor.run(installSignalHandlers=False)

    if not _reactor_thread:
        # Start the reactor in a separate thread.
        _reactor_thread = Thread(target=start, args=args, kwargs=kwargs)
        _reactor_thread.daemon = True
        _reactor_thread.start()


# Start the reactor; it will auto-stop at the end of the test suite.
start_reactor()


_socket = None


def http_setup(connectors, host, port, callback):
    # We just need to push an application context.
    application = web.Application(debug=True)

    # Invoke the callback if we got one.
    if callback:
        callback()
        reactor.callFromThread(callback)

    # Then import the resources; iterate and mount each one.
    module = force_import_module('tests.armet.connectors.resources')
    for name in module.__all__:
        getattr(module, name).mount(r'^/api', application)

    # Start the TCP listener.
    global _socket
    _socket = reactor.listenTCP(port, application, interface=host)


def http_teardown(host, port):
    # Stop listening on that port.
    threads.blockingCallFromThread(reactor, _socket.loseConnection)
