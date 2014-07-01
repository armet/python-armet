from armet.transcoders import TranscoderRegistry
import pytest


class ExampleEncoder:
    pass


class TestTranscoderRegistry:
    def setup(self):
        self.registry = TranscoderRegistry()
        self.registry.register(
            ExampleEncoder,
            names=['test', 'example'],
            mime_types=['application/octet-stream', 'test'])

    def teardown(self):
        self.registry.purge(ExampleEncoder)

    def test_lookup_by_mimetype(self):
        mime = 'test'
        assert self.registry.find(mime_type=mime) is ExampleEncoder

        mime = 'application/octet-stream'
        assert self.registry.find(mime_type=mime) is ExampleEncoder

    def test_lookup_by_name(self):
        assert self.registry.find(name='test') is ExampleEncoder
        assert self.registry.find(name='example') is ExampleEncoder

    def test_lookup_failure(self):
        assert pytest.raises(KeyError, self.registry.find, name='missing')
        assert pytest.raises(KeyError, self.registry.find, mime_type='missing')

    def test_lookup_bad_args(self):
        with pytest.raises(TypeError):
            self.registry.find()
