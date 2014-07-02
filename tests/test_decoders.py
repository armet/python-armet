from armet import decoders
import pytest


def test_decoders_api_methods():
    assert decoders.find
    assert decoders.register
    assert decoders.remove


class TestURLDecoder:

    def setup(self):
        self.decoder = decoders.find(name='url')()

    def test_decode_normal(self):
        data = 'foo=bar&bar=baz&fiz=buzz'

        expected = {
            'foo': 'bar',
            'bar': 'baz',
            'fiz': 'buzz'}

        assert self.decoder.decode(data) == expected

    def test_unable_to_decode(self):
        with pytest.raises(TypeError):
            self.decoder.decode([{'foo': 'bar'}])
