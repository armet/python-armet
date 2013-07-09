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

    def test_connectorless_abstract_resource(self, connectors):
        # Unset configuration.
        old = armet.use.config
        armet.use.config = {}

        class Resource(resources.Resource):
            class Meta:
                abstract = True

        assert Resource.meta.abstract

        # Reset the configuration
        armet.use.config = old


class TestResolution(BaseResourceTest):

    def test_super_direct_resource(self, connectors):
        response, content = self.client.get('/api/direct/')

        assert response.status == 200
        assert content.decode('utf8') == '42'

    def test_super_direct_model_resource(self, connectors):
        response, content = self.client.get('/api/model-direct/')

        assert response.status == 200
        assert content.decode('utf8') == '42'

    def test_super_indirect_resource(self, connectors):
        response, content = self.client.get('/api/indirect/')

        assert response.status == 200
        assert content.decode('utf8') == '84'

    def test_super_indirect_model_resource(self, connectors):
        response, content = self.client.get('/api/model-indirect/')

        assert response.status == 200
        assert content.decode('utf8') == '84'
