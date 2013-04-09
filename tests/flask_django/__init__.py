# -*- coding: utf-8 -*-
import six
import unittest
import wsgi_intercept
import os
from wsgi_intercept.httplib2_intercept import install


def setup():
    if six.PY3:
        # Neither flask nor werkzeug support python 3.x.
        raise unittest.SkipTest('No support for python 3.x')

    # Install the WSGI interception layer.
    install()

    # Ensure the settings are pointed to correctly.
    module = 'tests.{}.settings'.format('flask_django')
    os.environ["DJANGO_SETTINGS_MODULE"] = module

    # Set the WSGI application to intercept to.
    from .app import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)

    # Initialize the database tables.
    from django.db import connections, DEFAULT_DB_ALIAS
    connection = connections[DEFAULT_DB_ALIAS]
    connection.creation.create_test_db()

    # Install the test fixture.
    from django.core.management import call_command
    call_command('loaddata', 'test', verbosity=0, skip_validation=True)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
