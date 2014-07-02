from armet import decoders
import pytest


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
