# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
import armet
from armet import resources

# Request the generic models module inserted by the test runner.
models = sys.modules['tests.armet.connectors.models']

__all__ = [
    'SimpleResource',
    'PollResource',
    'StreamingResource',
    'AsyncResource',
    'AsyncStreamResource',
    'lightweight',
    'lightweight_streaming',
    'lightweight_async',
    'LeftResource',
    'RightResource',
    'echo',
    'cookie',
    'DirectResource',
    'IndirectResource',
    'ModelDirectResource',
    'ModelIndirectResource',
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


@armet.resource(methods='GET')
def lightweight(request, response):
    response.status = 412
    response['Content-Type'] = 'text/plain'
    response.write('Hello')


@armet.resource(methods='POST')
def lightweight(request, response):
    response.status = 414
    response['Content-Type'] = 'text/plain'
    response.write('Hello POST')


@armet.resource(methods='GET')
def lightweight_streaming(request, response):
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


@armet.asynchronous
@armet.resource(methods='GET')
def lightweight_async(request, response):
    def writer():
        response.status = 412
        response['Content-Type'] = 'text/plain'
        response.write('Hello')
        response.close()

    spawn(lightweight_async.meta.connectors, writer)


class PollResource(resources.ModelResource):

    class Meta:
        model = models.Poll

        slug = resources.IntegerAttribute('id')

    id = resources.IntegerAttribute('id')

    question = resources.TextAttribute('question')


class LeftResource(resources.Resource):

    class Meta:
        http_allowed_methods = ('HEAD', 'GET', 'OPTIONS',)
        http_allowed_origins = ('http://127.0.0.1:80',)
        http_allowed_headers = ('Content-Type', 'Content-MD5', 'Accept',)

    def get(self):
        # Do nothing.
        pass


class RightResource(resources.Resource):

    class Meta:
        http_allowed_methods = ('HEAD', 'GET', 'DELETE', 'OPTIONS',)
        http_allowed_origins = ('*',)
        http_allowed_headers = ('Content-Type', 'Content-MD5', 'Accept')

    def get(self):
        # Do nothing.
        pass


@armet.resource(methods='POST')
def echo(request, response):
    # Read in the given data in the given format.
    data = request.read(deserialize=True)

    # Write out the parsed data in the requested format.
    response.write(data, serialize=True)


@armet.resource(methods='GET')
def cookie(request, response):
    response['Content-Type'] = 'text/plain'
    response.write(request.cookies['blue'].value)


class DirectResource(resources.Resource):

    def route(self, request, response):
        return super(DirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'42')


class ModelDirectResource(resources.ModelResource):

    class Meta:
        model = models.Poll

    def route(self, request, response):
        return super(ModelDirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'42')


class IndirectResource(DirectResource):

    def route(self, request, response):
        return super(IndirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'84')


class ModelIndirectResource(ModelDirectResource):

    class Meta:
        model = models.Poll

    def route(self, request, response):
        return super(ModelIndirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'84')
