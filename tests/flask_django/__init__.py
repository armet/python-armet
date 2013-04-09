# -*- coding: utf-8 -*-
import six
import unittest
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install


def setup():
    if six.PY3:
        # Neither flask nor werkzeug support python 3.x.
        raise unittest.SkipTest('No support for python 3.x')

    # Install the WSGI interception layer.
    install()

    # Initialize the database access layer.
    from ..utils import django
    django.initialize('django')

    # Set the WSGI application to intercept to.
    from .app import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
