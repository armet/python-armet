""" ..
"""
import json
import mimeparse
from django.http import HttpResponse
from . import exceptions


class Encoder(object):
    #! Applicable mimetypes for this encoder.
    mimetypes = []

    @classmethod
    def get_mimetype(cls):
        """Returns the preferred mimetype."""
        return cls.mimetypes[0] if cls.mimetypes else None

    @classmethod
    def can_emit(cls, accept_header):
        """
        Determine if this Encoder can serialize an appropriate response to
        satisfy the ACCEPT header.
        """
        return mimeparse.best_match(cls.mimetypes, accept_header) != ''

    @classmethod
    def encode(self, obj=None):
            """Transforms python objects to an acceptable format for tansmission.
            response = HTTP
            """
            response = HttpResponse
            if obj is not None:
                # We have an object; we need to encode it and set content type, etc
                response.content = obj
                response['Content-Type'] = self.encoder.get_mimetype()

            # Pass on the constructed response
            return response

    @classmethod
    def __call__(cls, *args, **kwargs):
        return cls.encode(*args, **kwargs)


class Json(Encoder):
    #! Applicable mimetypes for this encoder.
    mimetypes = [
        # Offical; as per RFC 4627.
        'application/json',

        # Widely used (thanks <http://www.json.org/JSONRequest.html>.)
        'application/jsonrequest',

        # Miscellaneous mimetypes that are used frequently (incorrectly).
        'application/x-json',
        'text/json',

        # Widely used (incorrectly) thanks to ruby.
        'text/x-json',
    ]

    @classmethod
    def encode(cls, obj=None):
        return super(Json, cls).encode(json.dumps(obj))

        # Else; return nothing


# # TODO: JsonP
# class JsonP(Encoder):
#     #! Applicable mimetypes for this Encoder.
#     mimetypes = [
#         # Official; this is 'just' javascript.
#         'text/javascript',

#         # Miscellaneous mimetypes that are used frequently (incorrectly).
#         'application/javascript',
#         'application/x-javascript',
#         'text/x-javascript',
#     ]

    # TODO: emit()...

# TODO: Find a more fun way to keep track of Encoders
encoders = {
    'json': Json(),
}


def get_by_name(format):
    return encoders.get(format.lower())


def get_by_mimetype(mimetype):
    for serializer in encoders.values():
        if serializer.can_emit(mimetype):
            # Serializer matched against the accept header; return it
            return serializer

    # Nothing can be matched; return nothing


def get_available():
    available = {}
    for name, item in encoders.items():
        available[name] = item.get_mimetype()

    return available


def default():
    return Json


def find(request, **kwargs):
    """
    Determines the format to encode to and stores it upon success. Raises
    a proper exception if it cannot.
    """

    # Check locations where format may be defined in order of
    # precendence.
    if kwargs.get('format') is not None:
        # Format was provided through the URL via `.FORMAT`.
        encoder = get_by_name(kwargs['format'])

    elif request.META.get('HTTP_ACCEPT', None) is not None:
        # Use the encoding specified in the accept header
        encoder = get_by_mimetype(request.META['HTTP_ACCEPT'])

    else:
        # Default encoder
        encoder = Json

    if encoder is None:
        # Failed to find an appropriate encoder
        # Get dictionary of available formats
        available = get_available()

        # encode the response using the appropriate exception
        raise exceptions.NotAcceptable(available)

    return encoder
