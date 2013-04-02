# -*- coding: utf-8 -*-
# import multiprocessing
from .wsgi import application
from armet import test
import wsgi_intercept
import time

def setup():
    from wsgi_intercept.httplib2_intercept import install
    install()

    wsgi_intercept.add_wsgi_intercept('localhost', 5000, lambda: application)

def teardown():
    wsgi_intercept.remove_wsgi_intercept('localhost', 5000)
