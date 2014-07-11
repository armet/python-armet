import ujson as json

from ..codecs import JSONCodec
from . import register


@register(name="json", mime_type=JSONCodec.mime_types)
def decode(text):
    try:
        return json.loads(text)

    except ValueError as ex:
        raise TypeError from ex
