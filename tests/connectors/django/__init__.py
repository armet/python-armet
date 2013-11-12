# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import os
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install

# Setup the environment variables.
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.connectors.django.settings'

from .models import Poll

__all__ = [
    'Poll'
]


def http_setup(connectors, host, port, callback):
    # Setup the environment variables.
    os.environ['DJANGO_SETTINGS_MODULE'] = (
        'tests.connectors.django.settings')

    # Invoke the callback if we got one.
    if callback:
        callback()

    # Install the WSGI interception layer.
    install()

    # Import and grab the django application.
    from django.core.wsgi import get_wsgi_application

    # Enable the WSGI interception layer.
    wsgi_intercept.add_wsgi_intercept(host, port, get_wsgi_application)


def http_teardown(host, port):
    # Remove the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept(host, port)


def model_setup():
    # Setup the environment variables.
    os.environ['DJANGO_SETTINGS_MODULE'] = (
        'tests.connectors.django.settings')

    # Initialize the database and create all models.
    from django.db import connections, DEFAULT_DB_ALIAS
    connection = connections[DEFAULT_DB_ALIAS]
    connection.creation.create_test_db(verbosity=0)

    # Load the data fixture.
    from django.core import management
    data = os.path.join(os.path.dirname(__file__), '..', 'data.json')
    management.call_command('loaddata', data, verbosity=0, interactive=0)
