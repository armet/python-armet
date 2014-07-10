import json
from urllib.parse import parse_qs

from ..codecs import URLCodec
from . import register


# @register(name="url", mime_type=URLCodec.mime_types)
@register(name="url", mime_type=list(URLCodec.mime_types)[0])
def decode(text):
    try:
        data = parse_qs(text)
        return {k: v[0] if len(v) == 1 else v for k, v in data.items()}

    except AttributeError as ex:
        raise TypeError from ex
