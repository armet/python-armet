import json

from ..codecs import JSONCodec
from . import register


# @register(name="json", mime_types=JSONCodec.mime_types)
@register(name="json", mime_type="application/json")
def decode(text):
    try:
        return json.loads(text)

    except ValueError as ex:
        raise TypeError from ex
