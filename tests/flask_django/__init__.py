# -*- coding: utf-8 -*-
import six
import unittest
import wsgi_intercept
import os
import errno
from wsgi_intercept.httplib2_intercept import install


def setup():
    if six.PY3:
        # Neither flask nor werkzeug support python 3.x.
        raise unittest.SkipTest('No support for python 3.x')

    # Install the WSGI interception layer.
    install()

    # Ensure the settings are pointed to correctly.
    from django.conf import settings, Settings
    settings._wrapped = Settings('tests.flask_django.settings')
    settings._configure_logging()

    # Set the WSGI application to intercept to.
    from .app import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)

    # Initialize the database tables.
    # TODO: Figure out a way to use the ':memory:' database
    #   for this.
    try:
        # Destroy the existing database.
        os.remove(os.path.join(os.path.dirname(__file__), 'db.sqlite3'))

    except OSError as ex:
        if ex.errno == errno.ENOENT:
            # Database file didn't exist.
            pass

    # Initialize the database tables.
    from django.core import management
    management.call_command('syncdb', verbosity=1, interactive=False)

    # Install the test fixture.
    from django.core.management import call_command
    call_command('loaddata', 'test', verbosity=0, skip_validation=True)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
