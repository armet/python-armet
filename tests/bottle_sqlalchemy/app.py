# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from __future__ import absolute_import
from armet import resources, route
from armet.resources import attributes
from ..sqlalchemy import models
import bottle

# Instantiate the bottle application.
bottle.default_app.push()


# Configure armet globally to use the appropriate connectors.
class Meta:
    connectors = {'http': 'bottle', 'model': 'sqlalchemy'}


@route('/api/')
class SimpleResource(resources.ManagedResource):

    class Meta(Meta):
        pass

    def read(self):
        return None


@route('/api/')
class StreamingResource(resources.Resource):

    class Meta(Meta):
        pass

    def get(self):
        self.response['Content-Type'] = 'text/plain'
        yield 'this\n'
        self.response.write('where\n')
        self.response.flush()
        self.response.write('whence\n')
        yield
        yield 'that\n'
        self.response.write('why\n')
        yield 'and the other'


@route('/api/')
class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll
        engine = models.engine

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


@route('/api/')
class HttpWholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


@route('/api/')
class HttpForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


@route('/api/')
class WholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


@route('/api/')
class ForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


# Retrieve and store the configured bottle application.
application = bottle.default_app.pop()
