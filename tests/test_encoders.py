from armet import encoders
from collections import OrderedDict
import pytest


def test_encoders_api_methods():
    assert encoders.find
    assert encoders.register
    assert encoders.remove


class TestURLEncoder:

    def setup(self):
        self.encoder = encoders.find(name='url')()

    def test_encode_normal(self):
        data = OrderedDict((
            ('foo', 'bar'),
            ('bar', 'baz'),
            ('fiz', 'buzz')))

        expected = 'foo=bar&bar=baz&fiz=buzz'

        assert self.encoder.encode(data) == expected

    def test_unable_to_encode(self):
        with pytest.raises(TypeError):
            self.encoder.encode([{'foo': 'bar'}])
