# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from importlib import import_module
from wsgi_intercept.httplib2_intercept import install
import pytest
import armet
from armet import test


class BaseResourceTest(object):

    #! Host at which the intercept hook is installed.
    host = 'localhost'

    #! Port at which the intercept hook is installed.
    port = 5000

    @classmethod
    def setup_class(cls):
        # Initialize the test client.
        cls.client = test.Client(cls.host, cls.port)

    @pytest.fixture(autouse=True, scope='class')
    def initialize(self, request, connectors):
        # Install the WSGI interception layer.
        install()

        # Unload django.
        for module in list(sys.modules.keys()):
            if module and 'django' in module:
                del sys.modules[module]

        # Reset and clear all global cache in armet.
        from armet import decorators

        decorators._resources = {}
        # decorators._handlers = {}
        armet.use.config = {}

        # Re-initialize the configuration.
        armet.use(connectors=connectors, debug=True)

        prefix = 'tests.connectors.'
        callback = None
        if 'model' in connectors:
            # Initialize the database access layer.
            model = import_module(prefix + connectors['model'])
            callback = model.model_setup

            # Add the models module so that it can be generically imported.
            sys.modules[prefix + 'models'] = model
            request.cls.models = model

        # Initialize the http access layer.
        http = import_module(prefix + connectors['http'])
        http.http_setup(connectors, self.host, self.port, callback=callback)

        # Add a finalizer to teardown the http layer.
        request.addfinalizer(lambda: http.http_teardown(self.host, self.port))
