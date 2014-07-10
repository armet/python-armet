from armet import encoders
import json
from collections import OrderedDict
import pytest
from pytest import mark
from unittest import mock
from functools import reduce
import operator


def test_encoders_api_methods():
    assert encoders.find
    assert encoders.register
    assert encoders.remove


@mark.xfail
@mark.bench("encoders.register")
class TestEncoderRegisterDecorator:

    def test_register(self):
        mime = 'application/test'
        args = {
            'names': ['test'],
            'mime_types': [mime],
            'preferred_mime_type': mime,
        }

        @encoders.register(**args)
        def encoder_test(data, encoding):
            yield json.dumps(data).encode(encoding)

        encoder = encoders.find(name='test')
        assert encoder == encoder_test
        assert encoder.preferred_mime_type == mime

    def test_preferred_mime_type_fallback(self):
        @encoders.register(names=['test'])
        def encoder_test(data, encoding):
            yield json.dumps(data).encode(encoding)

        encoder = encoders.find(name='test')
        assert encoder.preferred_mime_type == 'text/plain'


class BaseEncoderTest:

    def encode(self, data):
        """Simple helper that makes encoder checking nicer."""
        encoded = reduce(operator.add, self.encoder(data, 'utf-8'))
        return encoded.decode('utf-8')


@mark.bench('self.encoder', iterations=10000)
class TestURLEncoder(BaseEncoderTest):

    def setup(self):
        self.encoder = encoders.find(name='url')

    def test_encode_normal(self):
        data = OrderedDict((
            ('foo', 'bar'),
            ('bar', 'baz'),
            ('fiz', 'buzz')))

        expected = 'foo=bar&bar=baz&fiz=buzz'

        assert self.encode(data) == expected

    def test_unable_to_encode(self):
        with pytest.raises(TypeError):
            self.encode([{'foo': 'bar'}])


@mark.bench('self.encoder', iterations=10000)
class TestJSONEncoder(BaseEncoderTest):

    def setup(self):
        self.encoder = encoders.find(name='json')

    def test_encode_scalar(self):
        data = False

        assert self.encode(data) == "[false]"

    def test_encode_null(self):
        data = None

        assert self.encode(data) == "[null]"

    def test_encode_large_simple_list(self):
        data = list(range(1, 10000))

        text = self.encode(data)
        assert json.loads(text) == data

    def test_encode_normal(self):
        data = OrderedDict([
            ('foo', 5),
            ('bar', None),
            ('baz', ['a', 'b', 'c']),
            ('bang', {'buzz': 'boop'})])

        expected = ('{"foo":5,"bar":null,"baz":["a","b","c"],'
                    '"bang":{"buzz":"boop"}}')

        assert self.encode(data) == expected

    def test_encode_failure(self):
        with pytest.raises(TypeError):
            self.encode({'foo': range(10)})


@mark.xfail
@mark.bench('self.encoder', iterations=10000)
class TestFormDataEncoder(BaseEncoderTest):

    def setup(self):
        self.encoder = encoders.find(name='form')

    def test_encode_normal(self):
        with mock.patch('armet.encoders.form.generate_boundary') as mocked:
            # Assert that the mocked function always returns the same value.
            mocked.return_value = 'abc123'

            data = OrderedDict((
                ('foo', 'bar'),
                ('bar', 'baz'),
                ('fiz', ['buzz', 'bang'])))

            expected = (
                '--abc123\r\n'
                'Content-Disposition: form-data; name=foo\r\n'
                '\r\n'
                'bar\r\n'
                '--abc123\r\n'
                'Content-Disposition: form-data; name=bar\r\n'
                '\r\n'
                'baz\r\n'
                '--abc123\r\n'
                'Content-Disposition: form-data; name=fiz\r\n'
                '\r\n'
                'buzz\r\n'
                '--abc123\r\n'
                'Content-Disposition: form-data; name=fiz\r\n'
                '\r\n'
                'bang\r\n'
                '--abc123--'
            )

            assert self.encode(data) == expected

    def test_encode_failure(self):
        with pytest.raises(TypeError):
            self.encode([{'a': 'b'}])

        with pytest.raises(TypeError):
            self.encode({'a': {'b': 'c'}})
