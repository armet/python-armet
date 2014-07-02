from armet import encoders
from collections import OrderedDict
import pytest


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
