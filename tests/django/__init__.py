# -*- coding: utf-8 -*-
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install


def setup():
    # Install the WSGI interception layer on top of httplib2.
    install()

    # Set the WSGI application to intercept to.
    from .wsgi import application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
