# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from cyclone import web
from twisted.internet import reactor
from threading import Thread
from importlib import import_module
from armet import resources


_reactor_thread = None


def stop_reactor():
    """Stop the Twisted reactor in the separate thread."""
    global _reactor_thread

    def stop():
        reactor.stop

    if _reactor_thread:
        reactor.callFromThread(stop)
        _reactor_thread.join(1)
        _reactor_thread = None


def start_reactor(*args, **kwargs):
    """
    Start the Twisted reactor in a separate thread so that it can
    run alongside the tests.
    """
    global _reactor_thread

    def run_this(*args, **kwargs):
        reactor.listenTCP(*args, **kwargs)
        reactor.run(installSignalHandlers=False)

    # Stop the reactor if it is already started.
    if _reactor_thread:
        stop_reactor()

    # Start the reactor in a separate thread.
    _reactor_thread = Thread(target=run_this, args=args, kwargs=kwargs)
    _reactor_thread.daemon = True
    _reactor_thread.start()


def setup(connectors, host, port):
    # Flask is pretty straightforward.
    # We just need to push an application context.
    application = web.Application()

    # Then import the resources; iterate and mount each one.
    for cls in import_module('tests.connectors.resources').__dict__.values():
        if isinstance(cls, type) and issubclass(cls, resources.Resource):
            cls.mount(r'^/api', application)

    # Spawn the reactor.
    start_reactor(port, application, interface=host)


def teardown(host, port):
    # Bring down the reactor.
    stop_reactor()
