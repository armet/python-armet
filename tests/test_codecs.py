from armet.codecs import CodecRegistry
import pytest


class ExampleEncoder:
    pass


class CounterExampleEncoder:
    pass


class TestCodecRegistry:
    def setup(self):
        self.registry = CodecRegistry()
        self.registry.register(
            ExampleEncoder,
            names=['test', 'example'],
            mime_types=['application/octet-stream', 'test/test'])

        self.registry.register(
            CounterExampleEncoder,
            mime_types=['application/xbel+xml', 'example/xml'])

    def test_lookup_by_mime_type(self):
        mime = 'test/test'
        assert self.registry.find(mime_type=mime) is ExampleEncoder

        mime = 'application/octet-stream'
        assert self.registry.find(mime_type=mime) is ExampleEncoder

    def test_lookup_by_media_range(self):
        mime = 'example/*;q=0.5,*/*; q=0.1'
        assert self.registry.find(media_range=mime) is CounterExampleEncoder

        mime = 'test/*;q=0.5,*/*; q=0.1'
        assert self.registry.find(media_range=mime) is ExampleEncoder

    def test_malformed_media_range(self):
        with pytest.raises(KeyError):
            self.registry.find(media_range='asdf')

    def test_lookup_by_name(self):
        assert self.registry.find(name='test') is ExampleEncoder
        assert self.registry.find(name='example') is ExampleEncoder

    def test_lookup_failure(self):
        assert pytest.raises(KeyError, self.registry.find, name='missing')
        mime = 'application/missing;q=0.5'
        assert pytest.raises(KeyError, self.registry.find, media_range=mime)

    def test_lookup_bad_args(self):
        with pytest.raises(TypeError):
            self.registry.find()
