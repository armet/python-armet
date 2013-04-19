# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install
import os


def setup():
    # Install the WSGI interception layer on top of httplib2.
    install()

    # Initialize the database access layer.
    from ..utils import sqlalchemy
    sqlalchemy.initialize()

    # Setup the environment variables.
    package = 'django_sqlalchemy'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.{}.settings'.format(package)

    # Set the WSGI application to intercept to.
    from django.core.wsgi import get_wsgi_application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, get_wsgi_application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
