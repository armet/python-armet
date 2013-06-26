# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import bottle
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install
from importlib import import_module
from armet import resources


def setup(connectors, host, port):
    # Install the WSGI interception layer.
    install()

    # Bottle is pretty straightforward.
    # We just need to push an application context.
    application = bottle.Bottle(__name__)

    # Then import the resources; iterate and mount each one.
    for cls in import_module('tests.connectors.resources').__dict__.values():
        if isinstance(cls, type) and issubclass(cls, resources.Resource):
            cls.mount(r'/api/', application)

    # Enable the WSGI interception layer.
    wsgi_intercept.add_wsgi_intercept(host, port, lambda: application)


def teardown(host, port):
    # Remove the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept(host, port)
