# -*- coding: utf-8 -*-
import armet
from armet import exceptions, resources
from .base import BaseResourceTest
import pytest


class TestResource(BaseResourceTest):

    def test_modelless_model_resource(self, connectors):
        with pytest.raises(exceptions.ImproperlyConfigured):
            class Resource(resources.ModelResource):
                pass

    def test_connectorless_resource(self, connectors):
        # Unset configuration.
        old = armet.use.config
        armet.use.config = {}

        with pytest.raises(exceptions.ImproperlyConfigured):
            class Resource(resources.Resource):
                pass

        # Reset the configuration
        armet.use.config = old
