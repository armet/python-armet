# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from armet import resources

# Request the generic models module inserted by the test runner.
models = sys.modules['tests.connectors.models']

__all__ = [
    'SimpleResource',
    'PollResource',
    'StreamingResource',
    'AsyncResource',
    'AsyncStreamResource'
]


class SimpleResource(resources.Resource):

    def get(self):
        # Do nothing and return nothing.
        pass


class StreamingResource(resources.Resource):

    def get(self):
        self.response.status = 412
        self.response['Content-Type'] = 'text/plain'

        yield 'this\n'

        self.response.write('where\n')
        self.response.flush()
        self.response.write('whence\n')

        yield
        yield 'that\n'

        self.response.write('why\n')

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

    def get(self):

        def writer():
            self.response.status = 412
            self.response['Content-Type'] = 'text/plain'
            self.response.write('Hello')
            self.response.close()

        spawn(self.meta.connectors, writer)


class AsyncStreamResource(resources.Resource):

    class Meta:
        asynchronous = True

    def get(self):

        def streamer():
            self.response.status = 412
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

        spawn(self.meta.connectors, streamer)


class PollResource(resources.ModelResource):

    class Meta:
        model = models.Poll

        slug = resources.IntegerAttribute('id')

    id = resources.IntegerAttribute('id')

    question = resources.TextAttribute('question')
