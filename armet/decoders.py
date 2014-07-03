from .codecs import CodecRegistry
import urllib.parse
import json
import io
import cgi
import operator


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


class FormDecoder:

    @classmethod
    def decode(cls, text, boundary):
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
