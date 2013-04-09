# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import wsgi_intercept
import os
from wsgi_intercept.httplib2_intercept import install


def setup():
    # Install the WSGI interception layer on top of httplib2.
    install()

    # Initialize the database access layer.
    from ..utils import django
    django.initialize('django_django')

    # Set the WSGI application to intercept to.
    from django.core.wsgi import get_wsgi_application
    wsgi_intercept.add_wsgi_intercept('localhost', 5000, get_wsgi_application)


def teardown():
    # Uninstall the WSGI interception layer.
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
