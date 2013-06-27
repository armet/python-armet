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

    @pytest.fixture(autouse=True, scope='session')
    def initialize(self, request, connectors):
        # Install the WSGI interception layer.
        install()

        # Remove the armet resources module so the resources
        # may be re-initialized.
        prefix = 'tests.connectors.'
        if (prefix + 'resources') in sys.modules:
            del sys.modules[prefix + 'resources']

        # Initialize armet configuration.
        armet.use(connectors=connectors, debug=True)

        # # Collect all loaded modules.
        # for name in set(sys.modules.keys()):
        #     for connector in connectors.values():
        #         if connector in name:
        #             del sys.modules[name]

        callback = None
        if 'model' in connectors:
            # Initialize the database access layer.
            model = import_module(prefix + connectors['model'])
            callback = model.model_setup

            # Add the models module so that it can be generically imported.
            sys.modules['tests.connectors.models'] = model

        # Initialize the http access layer.
        http = import_module(prefix + connectors['http'])
        http.http_setup(connectors, self.host, self.port, callback=callback)

        # Add a finalizer to teardown the http layer.
        request.addfinalizer(lambda: http.http_teardown(self.host, self.port))

        # Get all module names that were loaded by the connectors.
        # These need to be unloaded on teardown.
        # module_names = set(sys.modules.keys()) - module_names

        # # Construct a module finalizer to unload all of those modules.
        # def module_finalizer():
        #     for name in module_names:
        #         del sys.modules[name]

        # request.addfinalizer(module_finalizer)
