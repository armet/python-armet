from armet import decoders
import pytest
import json


def test_decoders_api_methods():
    assert decoders.find
    assert decoders.register
    assert decoders.remove


class TestURLDecoder:

    def setup(self):
        self.decode = decoders.find(name='url')

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


class TestJSONDecoder:
    def setup(self):
        self.decode = decoders.find(name='json')

    def test_encode_normal(self):
        data = {
            'foo': 5,
            'bar': None,
            'baz': ['a', 'b', 'c'],
            'bang': {'buzz': 'boop'}}

        assert self.decode(json.dumps(data)) == data

    def test_encode_failure(self):
        with pytest.raises(TypeError):
            self.decode('fail')
