from armet import encoders
from collections import OrderedDict
import pytest
from unittest import mock


def test_encoders_api_methods():
    assert encoders.find
    assert encoders.register
    assert encoders.remove


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


class TestJSONEncoder:
    def setup(self):
        self.encode = encoders.find(name='json')

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


class TestFormDataEncoder:
    def setup(self):
        self.encode = encoders.find(name='form')

    @mock.patch('armet.encoders.form.generate_boundary')
    def test_encode_normal(self, mocked):
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
