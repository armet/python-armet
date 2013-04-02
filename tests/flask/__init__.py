# -*- coding: utf-8 -*-
from .app import app
import wsgi_intercept


def setup():
    from wsgi_intercept.httplib2_intercept import install
    install()

    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: app)


def teardown():
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
