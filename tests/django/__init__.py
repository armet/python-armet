# -*- coding: utf-8 -*-
import wsgi_intercept
import os
import errno
from wsgi_intercept.httplib2_intercept import install


def setup():
    # Install the WSGI interception layer on top of httplib2.
    install()

    # Set the WSGI application to intercept to.
    from .wsgi import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)

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


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
