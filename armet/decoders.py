# from .codecs import CodecRegistry
from . import codecs
import urllib.parse
import json
import io
import cgi
import operator


# Create our encoder registry and pull methods off it for easy access.
_registry = codecs.CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register


@register(
    names=codecs.URLCodec.names,
    mime_types=codecs.URLCodec.mime_types)
def url_decode(text):
    try:
        data = urllib.parse.parse_qs(text)
        return {k: v[0] if len(v) == 1 else v for k, v in data.items()}

    except AttributeError as ex:
        raise TypeError from ex


@register(
    names=codecs.JSONCodec.names,
    mime_types=codecs.JSONCodec.mime_types)
def json_decode(text):
    try:
        return json.loads(text)
    except ValueError as ex:
        raise TypeError from ex


@register(
    names=codecs.FormDataCodec.names,
    mime_types=codecs.FormDataCodec.mime_types)
def form_decode(text, boundary):
    fp = io.BytesIO(text)
    result = cgi.parse_multipart(fp, {'boundary': boundary.encode('utf8')})

    # We need to operate on the values to decode them and to unpack shallow
    # ones.
    keys, values = zip(*result.items())

    # Decode the values
    decode = operator.methodcaller('decode', 'utf8')
    values = (list(map(decode, entry)) for entry in values)

    # Unpack shallow values (where there's only one)
    values = (x if len(x) > 1 else x[0] for x in values)

    # Return the dictionary!
    return dict(zip(keys, values))
