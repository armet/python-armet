from .codecs import CodecRegistry
import urllib.parse
import json


# Create our encoder registry and pull methods off it for easy access.
_registry = CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register


class URLDecoder:

    @classmethod
    def decode(cls, text):
        try:
            data = urllib.parse.parse_qs(text)
            return {k: v[0] if len(v) == 1 else v for k, v in data.items()}

        except AttributeError as ex:
            raise TypeError from ex


class JSONDecoder:

    @classmethod
    def decode(cls, text):
        try:
            return json.loads(text)
        except ValueError as ex:
            raise TypeError from ex
