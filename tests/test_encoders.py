from armet import encoders
import json
from collections import OrderedDict
import pytest
from pytest import mark
from unittest import mock


def test_encoders_api_methods():
    assert encoders.find
    assert encoders.register
    assert encoders.remove


@mark.bench('self.encode', iterations=10000)
class TestURLEncoder:

    def setup(self):
        self.encode = encoders.find(name='url')

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


@mark.bench('self.encode', iterations=10000)
class TestJSONEncoder:

    def setup(self):
        self.encode = encoders.find(name='json')

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


@mark.bench('self.encode', iterations=10000)
class TestFormDataEncoder:

    def setup(self):
        self.encode = encoders.find(name='form')

    def test_encode_normal(self):
        with mock.patch('armet.encoders.form.generate_boundary') as mocked:
            # Assert that the mocked function always returns the same value.
            mocked.return_value = 'abc123'

            data = OrderedDict((
                ('foo', 'bar'),
                ('bar', 'baz'),
                ('fiz', ['buzz', 'bang'])))

            expected = (
                b'--abc123\r\n'
                b'Content-Disposition: form-data; name=foo\r\n'
                b'\r\n'
                b'bar\r\n'
                b'--abc123\r\n'
                b'Content-Disposition: form-data; name=bar\r\n'
                b'\r\n'
                b'baz\r\n'
                b'--abc123\r\n'
                b'Content-Disposition: form-data; name=fiz\r\n'
                b'\r\n'
                b'buzz\r\n'
                b'--abc123\r\n'
                b'Content-Disposition: form-data; name=fiz\r\n'
                b'\r\n'
                b'bang\r\n'
                b'--abc123--'
            )

            assert self.encode(data) == expected

    def test_encode_failure(self):
        with pytest.raises(TypeError):
            self.encode([{'a': 'b'}])

        with pytest.raises(TypeError):
            self.encode({'a': {'b': 'c'}})
