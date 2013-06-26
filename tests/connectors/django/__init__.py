# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import os
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install


def setup(connectors, host, port):
    # Setup the environment variables.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.connectors.django.settings'

    # Install the WSGI interception layer.
    install()

    # Import and grab the django application.
    from django.core.wsgi import get_wsgi_application

    # Enable the WSGI interception layer.
    wsgi_intercept.add_wsgi_intercept(host, port, get_wsgi_application)


def teardown(host, port):
    # Remove the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept(host, port)
