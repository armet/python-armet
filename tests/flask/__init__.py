# -*- coding: utf-8 -*-
# import multiprocessing
from .app import app
from armet import test
import wsgi_intercept
import time

def setup():
    from wsgi_intercept.httplib2_intercept import install
    install()

    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: app)

def teardown():
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
