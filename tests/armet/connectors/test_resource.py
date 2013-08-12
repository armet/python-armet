# -*- coding: utf-8 -*-
import armet
from armet import exceptions, resources
from .base import BaseResourceTest
import pytest
import json


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


class TestAllowed(BaseResourceTest):

    def test_http_allowed_methods(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                http_allowed_methods = 'GET',

        meta = Resource.meta

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods

    def test_http_allowed_methods_to_operations(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                http_allowed_methods = 'GET',

        meta = Resource.meta

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods

        assert 'read' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations
        assert 'read' in meta.allowed_operations

    def test_allowed_operations(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                allowed_operations = 'read',

        meta = Resource.meta

        assert 'read' in meta.allowed_operations
        assert 'read' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations

    def test_allowed_operations_to_methods(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                allowed_operations = 'read',

        meta = Resource.meta

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods

        assert 'read' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations
        assert 'read' in meta.allowed_operations

    def test_allowed_methods_list(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                http_allowed_methods = 'GET',

                http_list_allowed_methods = 'PUT',

        meta = Resource.meta

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' not in meta.http_list_allowed_methods
        assert 'PUT' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods

    def test_allowed_methods_list_to_operations(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                http_allowed_methods = 'GET',

                http_list_allowed_methods = 'PUT',

        meta = Resource.meta

        assert 'read' in meta.allowed_operations
        assert 'read' not in meta.list_allowed_operations
        assert 'update' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' not in meta.http_list_allowed_methods
        assert 'PUT' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods

    def test_allowed_operations_list(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                allowed_operations = 'read',

                list_allowed_operations = 'update',

        meta = Resource.meta

        assert 'read' in meta.allowed_operations
        assert 'read' not in meta.list_allowed_operations
        assert 'update' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations

    def test_allowed_operations_list_to_methods(self):

        class Resource(resources.ModelResource):

            class Meta:
                abstract = True

                allowed_operations = 'read',

                list_allowed_operations = 'update',

        meta = Resource.meta

        assert 'read' in meta.allowed_operations
        assert 'read' not in meta.list_allowed_operations
        assert 'update' in meta.list_allowed_operations
        assert 'read' in meta.detail_allowed_operations

        assert 'GET' in meta.http_allowed_methods
        assert 'GET' not in meta.http_list_allowed_methods
        assert 'PUT' in meta.http_list_allowed_methods
        assert 'GET' in meta.http_detail_allowed_methods


class TestResolution(BaseResourceTest):

    def test_super_direct_resource(self, connectors):
        response, content = self.client.get('/api/direct/')

        assert response.status == 200
        assert content.decode('utf8') == '42'

    def test_super_direct_model_resource(self, connectors):
        response, content = self.client.get('/api/model-direct/')

        assert response.status == 200

        data = json.loads(content.decode('utf8'))

        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_super_indirect_resource(self, connectors):
        response, content = self.client.get('/api/indirect/')

        assert response.status == 200
        assert content.decode('utf8') == '84'

    def test_super_indirect_model_resource(self, connectors):
        response, content = self.client.get('/api/model-indirect/')

        assert response.status == 200

        data = json.loads(content.decode('utf8'))

        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_super_twice_indirect_resource(self, connectors):
        response, content = self.client.get('/api/twice-indirect/')

        assert response.status == 200
        assert content.decode('utf8') == '84'

    def test_super_twice_indirect_model_resource(self, connectors):
        response, content = self.client.get('/api/model-twice-indirect/')

        assert response.status == 200

        data = json.loads(content.decode('utf8'))

        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_super_thrice_indirect_resource(self, connectors):
        response, content = self.client.get('/api/thrice-indirect/')

        assert response.status == 200
        assert content.decode('utf8') == '84'

    def test_super_thrice_indirect_model_resource(self, connectors):
        response, content = self.client.get('/api/model-thrice-indirect/')

        assert response.status == 200

        data = json.loads(content.decode('utf8'))

        assert data[0]['question'] == 'Are you an innie or an outie?'

    def test_mixin_resource(self, connectors):
        response, content = self.client.get('/api/mixin/')

        assert response.status == 200
        assert content.decode('utf8') == 'Hello'
