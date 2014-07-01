from armet import encoders
import pytest


class ExampleEncoder:
    pass


class TestEncoderLookup:
    def setup(self):
        encoders.register(
            ExampleEncoder,
            names=['test', 'example'],
            mime_types=['application/octet-stream', 'test'])

    def teardown(self):
        encoders.purge(ExampleEncoder)

    def test_lookup_by_mimetype(self):
        mime = 'test'
        assert encoders.find(mime_type=mime) is ExampleEncoder

        mime = 'application/octet-stream'
        assert encoders.find(mime_type=mime) is ExampleEncoder

    def test_lookup_by_name(self):
        assert encoders.find(name='test') is ExampleEncoder
        assert encoders.find(name='example') is ExampleEncoder

    def test_lookup_failure(self):
        assert pytest.raises(KeyError, encoders.find, name='missing')
        assert pytest.raises(KeyError, encoders.find, mime_type='missing')

    def test_lookup_bad_args(self):
        with pytest.raises(TypeError):
            encoders.find()
