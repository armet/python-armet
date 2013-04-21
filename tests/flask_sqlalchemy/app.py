# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from __future__ import absolute_import
from flask import Flask
from ..sqlalchemy import models
import armet
from armet import resources
from armet.resources import attributes
import gevent


# Instantiate the flask application.
application = Flask(__name__)


class Meta:
    connectors = {
        'http': 'flask',
        'model': 'sqlalchemy'
    }


@armet.route('/api/', application)
class SimpleResource(resources.ManagedResource):

    class Meta(Meta):
        pass

    def read(self):
        return None


@armet.route('/api/', application)
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


@armet.route('/api/', application)
class AsyncResource(resources.Resource):

    class Meta(Meta):
        asynchronous = True

    def get(self):
        def spawn():
            self.response.status = 202
            self.response['Content-Type'] = 'text/plain'
            self.response.write('Hello')
            self.response.close()
        gevent.spawn(spawn)


@armet.route('/api/', application)
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
        gevent.spawn(spawn_stream)


@armet.route('/api/', application)
class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll
        engine = models.engine

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


@armet.route('/api/', application)
class HttpWholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


@armet.route('/api/', application)
class HttpForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


@armet.route('/api/', application)
class WholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


@armet.route('/api/', application)
class ForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)
