import json
from collections import Iterable

from ..codecs import JSONCodec
from ..utils import chunk
from . import register


@register(name="json", mime_type=JSONCodec.mime_types)
def encode(data, encoding):
    # Ensure that the scalar data is wrapped in a list as
    # a valid JSON document be an object or a list.
    # See: http://tools.ietf.org/html/rfc4627
    if isinstance(data, str) or not isinstance(data, Iterable):
        data = [data]

    # Separators are used here to assert that no uneccesary spaces are
    # added to the json.
    data = json.dumps(data, separators=(',', ':'))

    # TODO: Replace this with real json streaming
    return chunk(data.encode(encoding))
