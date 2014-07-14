from armet import decoders
import pytest
from pytest import mark
import json


def test_decoders_api_methods():
    assert decoders.find
    assert decoders.register
    assert decoders.remove


@mark.bench('self.decode', iterations=10000)
class TestURLDecoder:

    def setup(self):
        self.decode, _ = decoders.find(name='url')

    def test_decode_normal(self):
        data = 'foo=bar&bar=baz&fiz=buzz'

        expected = {
            'foo': 'bar',
            'bar': 'baz',
            'fiz': 'buzz'}

        assert self.decode(data) == expected

    def test_decode_object(self):
        with pytest.raises(TypeError):
            self.decode([{'foo': 'bar'}])


@mark.bench('self.decode', iterations=10000)
class TestJSONDecoder:

    def setup(self):
        self.decode,  _ = decoders.find(name='json')

    def test_decode_normal(self):
        data = {
            'foo': 5,
            'bar': None,
            'baz': ['a', 'b', 'c'],
            'bang': {'buzz': 'boop'}}

        assert self.decode(json.dumps(data)) == data

    def test_decode_failure(self):
        with pytest.raises(TypeError):
            self.decode('fail')


@mark.bench('self.decode', iterations=10000)
class TestFormDecoder:

    def setup(self):
        self.decode,  _ = decoders.find(name='form')

    def test_decode_normal(self):
        boundary = 'abc123'

        data = (
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

        expected = {
            'foo': 'bar',
            'bar': 'baz',
            'fiz': ['buzz', 'bang']
        }

        assert self.decode(data, boundary=boundary) == expected
