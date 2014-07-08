from armet import codecs
from itertools import chain, repeat
from urllib.parse import urlencode
from collections import Iterable
import json


class Encoder(codecs.Codec):
    """Wraps encoders to provide additonal decorator functionality."""

    def __init__(self, *args, preferred_mime_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Make an attempt to get a random preferred mime type.
        # Fallback to plain text if no mimetypes were defined for this.
        if preferred_mime_type is None:
            preferred_mime_type = next(iter(self.mime_types), 'text/plain')
        self.preferred_mime_type = preferred_mime_type

# Create our encoder registry and pull methods off it for easy access.
_registry = codecs.CodecRegistry(Encoder)

find = _registry.find
remove = _registry.remove
register = _registry.register


def _chunk(data, chunk_size=16*1024):
    """Simple chunking function to easily make encoders into generators.

    Invocations of this should be replaced when more streaming-friendly
    encoders are implemented.
    """
    while True:
        buf = data[:chunk_size]
        data = data[chunk_size:]
        if not buf:
            break
        yield buf


@register(
    names=codecs.URLCodec.names,
    mime_types=codecs.URLCodec.mime_types,
    preferred_mime_type=codecs.URLCodec.preferred_mime_type)
def url_encoder(data, encoding):
    try:
        # Normalize the encode so that users pay invoke using either
        # {"foo": "bar"} or {"foo": ["bar", "baz"]}.
        data = list(chain.from_iterable(
            ((k, v),) if isinstance(v, str) else zip(repeat(k), v)
            for k, v in data.items()))

    except AttributeError as ex:
        raise TypeError from ex

    # URL encode it and return a streamable generator.
    # TODO: Replace this with actual url encoded streaming.
    return _chunk(urlencode(data).encode(encoding))


@register(
    names=codecs.JSONCodec.names,
    mime_types=codecs.JSONCodec.mime_types,
    preferred_mime_type=codecs.JSONCodec.preferred_mime_type)
def json_encoder(data, encoding):
    # Ensure that the scalar data is wrapped in a list as
    # a valid JSON document must be an object or a list.
    # See: http://tools.ietf.org/html/rfc4627
    if isinstance(data, str) or not isinstance(data, Iterable):
        data = [data]

    # Separators are used here to assert that no uneccesary spaces are
    # added to the json.
    data = json.dumps(data, separators=(',', ':'))

    # TODO: Replace this with real json streaming
    return _chunk(data.encode(encoding))
