# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import resources
from armet.resources import attributes
from ..sqlalchemy import models


class Meta:
    connectors = {
        'http': 'django',
        'model': 'sqlalchemy'
    }


class SimpleResource(resources.Resource):

    class Meta(Meta):
        pass

    def read(self):
        return None


class WrongResource(resources.ModelResource):

    class Meta:
        model = models.Poll
        engine = models.engine
        connectors = {'http': 'flask'}


class PollResource(WrongResource):

    class Meta(Meta):
        pass

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


class HttpWholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


class HttpForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


class WholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


class ForbiddenResource(resources.Resource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)
