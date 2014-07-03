from armet import encoders
import json
from collections import OrderedDict
import pytest
from pytest import mark


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
