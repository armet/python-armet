# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from __future__ import absolute_import
from armet import resources
from armet.resources import attributes
from ..django import models
from cyclone import web
from twisted.internet import reactor


# Configure armet globally to use the appropriate connectors.
class Meta:
    connectors = {'http': 'cyclone', 'model': 'django'}


class SimpleResource(resources.ManagedResource):

    class Meta(Meta):
        pass

    def read(self):
        return None


class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


class StreamingResource(resources.Resource):

    class Meta(Meta):
        pass

    def get(self):
        self.response.status = 202
        self.response['Content-Type'] = 'text/plain'
        yield 'this\n'
        self.response.write('where\n')
        self.response.flush()
        self.response.write('whence\n')
        yield
        yield 'that\n'
        self.response.write('why\n')
        yield 'and the other'


class AsyncResource(resources.Resource):

    class Meta(Meta):
        asynchronous = True

    def get(self):
        def spawn():
            self.response.status = 202
            self.response['Content-Type'] = 'text/plain'
            self.response.write('Hello')
            self.response.close()
        reactor.callLater(0, spawn)


class AsyncStreamResource(resources.Resource):

    class Meta(Meta):
        asynchronous = True

    def get(self):
        def spawn_stream():
            self.response.status = 202
            self.response['Content-Type'] = 'text/plain'
            self.response.write('this\n')
            self.response.flush()
            self.response.write('where\n')
            self.response.flush()
            self.response.write('whence\n')
            self.response.write('that\n')
            self.response.flush()
            self.response.write('why\n')
            self.response.write('and the other')
            self.response.close()
        reactor.callLater(0, spawn_stream)


class HttpWholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


class HttpForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


class WholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


class ForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


# Export the cyclone application.
application = web.Application(debug=True)

# Mount the urls on the application.
mount = r'^/api'
SimpleResource.mount(mount, application)
StreamingResource.mount(mount, application)
AsyncResource.mount(mount, application)
AsyncStreamResource.mount(mount, application)
PollResource.mount(mount, application)
HttpWholeForbiddenResource.mount(mount, application)
HttpForbiddenResource.mount(mount, application)
WholeForbiddenResource.mount(mount, application)
ForbiddenResource.mount(mount, application)
