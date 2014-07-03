from armet.codecs import CodecRegistry
from itertools import chain, repeat
from urllib.parse import urlencode
from collections import Iterable
import json


# Create our encoder registry and pull methods off it for easy access.
_registry = CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register


class URLEncoder:

    @classmethod
    def encode(cls, data):
        try:
            # Normalize the encode so that users pay invoke using either
            # {"foo": "bar"} or {"foo": ["bar", "baz"]}.
            return urlencode(list(chain.from_iterable(
                ((k, v),) if isinstance(v, str) else zip(repeat(k), v)
                for k, v in data.items())))

        except AttributeError as ex:
            raise TypeError from ex


class JSONEncoder:

    @classmethod
    def encode(cls, data):
        # Ensure that the scalar data is wrapped in a list as
        # a valid JSON document must be an object or a list.
        # See: http://tools.ietf.org/html/rfc4627
        if isinstance(data, str) or not isinstance(data, Iterable):
            data = [data]

        # Separators are used here to assert that no uneccesary spaces are
        # added to the json.
        return json.dumps(data, separators=(',', ':'))
