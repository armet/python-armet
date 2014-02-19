# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
import json
import armet
from armet import resources, attributes, exceptions

# Request the generic models module inserted by the test runner.
models = sys.modules['tests.connectors.models']

__all__ = [
    'SimpleResource',
    'SimpleTrailingResource',
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
    'ModelDirectResource',
    'IndirectResource',
    'ModelIndirectResource',
    'TwiceIndirectResource',
    'ModelTwiceIndirectResource',
    'ThriceIndirectResource',
    'ModelThriceIndirectResource',
    'MixinResource',
    'PollExcludeResource',
    'PollUnreadResource',
    'PollUnwriteResource',
    'PollNoNullResource',
    'PollRequiredResource',
    'PollValidResource',
    'PollNamedResource',
    'DirectConnectorResource',
    'IndirectConnectorResource',
    'TwiceIndirectConnectorResource',
    'ThriceIndirectConnectorResource',
    'DirectModelConnectorResource',
    'IndirectModelConnectorResource',
    'TwiceIndirectModelConnectorResource',
    'ThriceIndirectModelConnectorResource',
    'DirectModelConnectorMixinResource',
    'IndirectModelConnectorMixinResource',
    'TwiceIndirectModelConnectorMixinResource',
    'ThriceIndirectModelConnectorMixinResource',
]


class SimpleResource(resources.Resource):

    def get(self, request, response):
        # Do nothing and return nothing.
        pass


class SimpleTrailingResource(resources.Resource):

    class Meta:
        trailing_slash = False

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

        slug = 'id'

    id = attributes.IntegerAttribute('id')

    question = attributes.TextAttribute('question')

    available = attributes.BooleanAttribute('available')


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

    id = attributes.IntegerAttribute('id')

    question = attributes.TextAttribute('question')

    def route(self, request, response):
        return super(ModelDirectResource, self).route(request, response)


class IndirectResource(DirectResource):

    def route(self, request, response):
        return super(IndirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'84')


class ModelIndirectResource(ModelDirectResource):

    class Meta:
        model = models.Poll

    def read(self):
        return super(ModelIndirectResource, self).read()


class TwiceIndirectResource(IndirectResource):

    def route(self, request, response):
        return super(TwiceIndirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'84')


class ModelTwiceIndirectResource(ModelIndirectResource):

    class Meta:
        model = models.Poll

    def read(self):
        return super(ModelTwiceIndirectResource, self).read()


class ThriceIndirectResource(IndirectResource):

    def route(self, request, response):
        return super(ThriceIndirectResource, self).route(request, response)

    def get(self, request, response):
        response.write(b'84')


class ModelThriceIndirectResource(ModelIndirectResource):

    class Meta:
        model = models.Poll

    def read(self):
        return super(ModelThriceIndirectResource, self).read()


class ExtraStuff(object):

    def dispatch(self, *args):
        self.content = b'Hello'
        return super(ExtraStuff, self).dispatch(*args)


class MixinResource(ExtraStuff, IndirectResource):

    content = b'World'

    def route(self, request, response):
        return super(MixinResource, self).route(request, response)

    def get(self, request, response):
        response.write(self.content)


class PollExcludeResource(PollResource):

    question = attributes.TextAttribute('question', include=False)


class PollUnreadResource(PollResource):

    question = attributes.TextAttribute('question', read=False)


class PollUnwriteResource(PollResource):

    question = attributes.TextAttribute('question', write=False)


class PollNoNullResource(PollResource):

    question = attributes.TextAttribute('question', null=False)


class PollRequiredResource(PollResource):

    question = attributes.TextAttribute('question', required=True)


class PollNamedResource(PollResource):

    question = attributes.TextAttribute('question', name='superQuestion')


class PollValidResource(PollResource):

    votes = attributes.IntegerAttribute('votes')

    def clean_votes(self, value):
        assert value > 0, 'Must be greater than 0.'
        assert value < 51, 'Must be less than 51.'
        return value

    def clean_question(self, value):
        errors = []

        if len(value) <= 15:
            errors.append('Must be more than 15 characters.')

        if value.find('?') == -1:
            errors.append('Must have at least one question mark.')

        if errors:
            raise exceptions.ValidationError(*errors)

        return value


class DirectConnectorResource(resources.Resource):

    @classmethod
    def view(cls, *args, **kwargs):
        cls.status = 205
        return super(DirectConnectorResource, cls).view(*args, **kwargs)

    def get(self, request, response):
        response.status = self.status
        response.write(b'Hello World\n')


class IndirectConnectorResource(DirectConnectorResource):
    pass


class TwiceIndirectConnectorResource(IndirectConnectorResource):
    pass


class ThriceIndirectConnectorResource(TwiceIndirectConnectorResource):
    pass


class DirectModelConnectorResource(resources.ModelResource):

    class Meta:
        model = models.Poll

    id = attributes.IntegerAttribute('id')

    def route(self, request, response):
        response.status = 205
        return super(DirectModelConnectorResource, self).route(
            request, response)

    def get(self, request, response):
        response.write(json.dumps(self.read()).encode('utf8'))

    def read(self):
        return ['Hello', 'World']


class IndirectModelConnectorResource(DirectModelConnectorResource):
    pass


class TwiceIndirectModelConnectorResource(IndirectModelConnectorResource):
    pass


class ThriceIndirectModelConnectorResource(
        TwiceIndirectModelConnectorResource):
    pass


class DirectModelConnectorMixin(object):

    def destroy(self):
        self.response.status = 402
        return None


class DirectModelConnectorMixinResource(
        DirectModelConnectorMixin, resources.ModelResource):

    class Meta:
        model = models.Poll

    id = attributes.IntegerAttribute('id')

    def delete(self, request, response):
        self.response.status = 405
        self.destroy()


class IndirectModelConnectorMixinResource(DirectModelConnectorMixinResource):
    pass


class TwiceIndirectModelConnectorMixinResource(
        IndirectModelConnectorMixinResource):
    pass


class ThriceIndirectModelConnectorMixinResource(
        TwiceIndirectModelConnectorMixinResource):
    pass
