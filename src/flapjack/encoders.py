""" ..
"""
import json
from .http import HttpResponse
from . import exceptions, transcoders


class Encoder(transcoders.Transcoder):

    @classmethod
    def encode(cls, obj=None):
        """
        Transforms objects into an acceptable format for tansmission.

        @returns
            An HttpResponse object containing all neccessary information
            that can be provided.
        """
        response = HttpResponse()
        if obj is not None:
            # We have an object; we need to encode it and set content
            # type, etc
            response.content = obj
            response['Content-Type'] = cls.mimetype

        # Pass on the constructed response
        return response


@Encoder.register()
class Text(transcoders.Text, Encoder):

    @staticmethod
    def _encode_value(value):
        return str(value) if value is not None else ''

    @staticmethod
    def _encode_item(item):
        return '\n'.join(
            ' '.join((x, Text._encode_value(y))) for x, y in item.items())

    @classmethod
    def encode(cls, obj=None):
        if isinstance(obj, list):
            # Encode all the items
            text = '\n\n'.join(Text._encode_item(x) for x in obj)
        else:
            # Encode just the one item
            text = Text._encode_item(obj)

        return super(Text, cls).encode(text)


@Encoder.register()
class Json(transcoders.Json, Encoder):

    @classmethod
    def encode(cls, obj=None):
        return super(Json, cls).encode(json.dumps(obj))


def find(request, format=None):
    """Determines the format to encode to and returns the encoder."""
    # Check locations where format may be defined in order of
    # precendence.
    if format is not None:
        # Format was provided through the URL via `.FORMAT`.
        format = format.lower()
        if format in Encoder.registry:
            return Encoder.registry[format]

        # Format was provided but unknown to us; we can do nothing in
        # this case

    elif request.META.get('HTTP_ACCEPT', None) is not None:
        # Use the encoding specified in the accept header
        encoder = Encoder.get(request.META['HTTP_ACCEPT'])
        if encoder is not None:
            return encoder

    # Failed to find an appropriate encoder
    # Get dictionary of available formats
    available = {k: v.mimetype for k, v in Encoder.registry.items()}

    # Encode the response using the appropriate exception
    raise exceptions.NotAcceptable(Text.encode(available))
