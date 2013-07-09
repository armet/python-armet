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

    # isinstance with direct inheritance from resources.Resource
    # isinstance with direct inheritance from resources.ModelResource
    # isinstance with indirect inheritance from resources.Resource
    # isinstance with indirect inheritance from resources.ModelResource
    # issubclass with direct inheritance from resources.Resource
    # issubclass with direct inheritance from resources.ModelResource
    # issubclass with indirect inheritance from resources.Resource
    # issubclass with indirect inheritance from resources.ModelResource
    # super on direct inheritance from resources.Resource
    # super on direct inheritance from resources.ModelResource
    # super on indirect inheritance from resources.Resource
    # super on indirect inheritance from resources.ModelResource

    pass
