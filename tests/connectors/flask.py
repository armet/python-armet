# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import flask
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install
from importlib import import_module
from armet import resources


def http_setup(connectors, host, port):
    # Install the WSGI interception layer.
    install()

    # Flask is pretty straightforward.
    # We just need to push an application context.
    application = flask.Flask(__name__)
    application.debug = True

    # Then import the resources; iterate and mount each one.
    module = import_module('tests.connectors.resources')
    for name in module.__all__:
        getattr(module, name).mount(r'/api/', application)

    # Enable the WSGI interception layer.
    wsgi_intercept.add_wsgi_intercept(host, port, lambda: application)


def http_teardown(host, port):
    # Remove the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept(host, port)
