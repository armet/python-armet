from . import codecs, utils
import urllib.parse


# Create our encoder registry and pull methods off it for easy access.
# Note that all encoders defined in armet.encoders are added to the registry
# automatically.
_registry = codecs.CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register


class Encoder:
    """The base class for armet's encoders."""

    # The codec class for this encoder.  Note that the codec must provide
    # preferred_mime_type, mime_types, and names in order for this to function
    # properly.
    _codec = codecs.Codec

    @utils.classproperty
    def preferred_mime_type(self):
        return self._codec.preferred_mime_type

    @utils.classproperty
    def mime_types(self):
        return self._codec.mime_types

    @utils.classproperty
    def names(self):
        return self._codec.names

    def encode(self, data):
        """Encode the passed data and return the encoded version.
        May raise a TypeError if unable to encode the type passed in.
        """
        raise NotImplementedError


class URLEncoder(Encoder):

    _codec = codecs.URLCodec

    def encode(self, data):
        return urllib.parse.urlencode(data)
