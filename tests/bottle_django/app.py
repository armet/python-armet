# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
from armet import resources, route
from armet.resources import attributes
from ..django import models
import bottle

# Instantiate the bottle application.
bottle.default_app.push()


# Configure armet globally to use the appropriate connectors.
class Meta:
    connectors = {'http': 'bottle', 'model': 'django'}


@route('/api/')
class SimpleResource(resources.Resource):

    class Meta(Meta):
        pass

    def read(self):
        return None


@route('/api/')
class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


@route('/api/')
class HttpWholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


@route('/api/')
class HttpForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


@route('/api/')
class WholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


@route('/api/')
class ForbiddenResource(resources.Resource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


# Retrieve and store the configured bottle application.
application = bottle.default_app.pop()
