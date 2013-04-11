# -*- coding: utf-8 -*-
import six
import unittest
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install


def setup():
    # Install the WSGI interception layer.
    install()

    # Initialize the database access layer.
    from ..utils import django
    django.initialize('django')

    # Ensure debugging is turned on.
    from bottle import debug
    debug()

    # Set the WSGI application to intercept to.
    from .app import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
