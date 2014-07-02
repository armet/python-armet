from . import codecs, utils
import urllib.parse


# Create our encoder registry and pull methods off it for easy access.
_registry = codecs.CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register


class Decoder:

    # The codec class for this decoder.  Note that the codec must provide
    # mime_types and names.
    _codec = codecs.Codec

    @utils.classproperty
    def mime_types(cls):
        return cls._codec.mime_types

    @utils.classproperty
    def names(cls):
        return cls._codec.names

    def decode(self, data):
        """Decode the data passed in, This function will raise a TypeError
        if unable to parse or decode the data passed in."""
        raise NotImplementedError


class URLDecoder(Decoder):

    _codec = codecs.URLCodec

    def decode(self, data):
        return urllib.parse.parse_qs(data)
