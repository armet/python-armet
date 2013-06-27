# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
import armet
from armet import resources

# Request the generic models module inserted by the test runner.
models = sys.modules['tests.connectors.models']

__all__ = [
    'SimpleResource',
    'PollResource',
    'StreamingResource',
    'AsyncResource',
    'AsyncStreamResource',
    'lightweight'
]


class SimpleResource(resources.Resource):

    def get(self, request, response):
        # Do nothing and return nothing.
        pass


class StreamingResource(resources.Resource):

    def get(self, request, response):
        response.status = 412
        response['Content-Type'] = 'text/plain'

        yield 'this\n'

        response.write('where\n')
        response.flush()
        response.write('whence\n')

        yield
        yield 'that\n'

        response.write('why\n')

        yield 'and the other'


def spawn(connectors, function):
    if 'cyclone' in connectors['http']:
        from twisted.internet import reactor
        reactor.callLater(0, function)

    else:
        import gevent
        gevent.spawn(function)


class AsyncResource(resources.Resource):

    class Meta:
        asynchronous = True

    def get(self, request, response):

        def writer():
            response.status = 412
            response['Content-Type'] = 'text/plain'
            response.write('Hello')
            response.close()

        spawn(self.meta.connectors, writer)


class AsyncStreamResource(resources.Resource):

    class Meta:
        asynchronous = True

    def get(self, request, response):

        def streamer():
            response.status = 412
            response['Content-Type'] = 'text/plain'
            response.write('this\n')
            response.flush()

            response.write('where\n')
            response.flush()

            response.write('whence\n')
            response.write('that\n')
            response.flush()

            response.write('why\n')
            response.write('and the other')
            response.close()

        spawn(self.meta.connectors, streamer)


@armet.resource(method='GET')
def lightweight(request, response):
    response.status = 412
    response['Content-Type'] = 'text/plain'
    response.write('Hello')


class PollResource(resources.ModelResource):

    class Meta:
        model = models.Poll

        slug = resources.IntegerAttribute('id')

    id = resources.IntegerAttribute('id')

    question = resources.TextAttribute('question')
