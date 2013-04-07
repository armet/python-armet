# -*- coding: utf-8 -*-
from armet import resources
from armet.resources import attributes
from . import models


class SimpleResource(resources.Resource):

    class Meta:
        connectors = {'http': 'django'}

    def read(self):
        return None


class PollResource(resources.ModelResource):

    class Meta:
        connectors = {'http': 'django', 'model': 'django'}
        model = models.Poll

    question = attributes.Attribute('question')


class HttpWholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'django'}
        http_allowed_methods = ('GET', 'DELETE',)


class HttpForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'django'}
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


class WholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'django'}
        allowed_operations = ('read', 'destroy',)


class ForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'django'}
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)
