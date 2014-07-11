from itertools import chain, repeat
from urllib.parse import urlencode

from ..codecs import URLCodec
from ..utils import chunk
from . import register


@register(name="url", mime_type=URLCodec.mime_types,
          preferred_mime_type=URLCodec.preferred_mime_type)
def encode(data, encoding):
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
    return chunk(urlencode(data).encode(encoding))
