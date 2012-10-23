""" ..
"""
import json
import mimeparse
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
    def encode(cls, obj):
        if obj is not None:
            # Only emit something when we get something
            return json.dumps(obj)

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
    'json': Json,
    # 'jsonp': JsonP
}


def get_by_name(format):
    return encoders.get(format.lower())


def get_by_request(request):
    if 'HTTP_ACCEPT' not in request.META:
        # No accept header provided; default to JSON
        return encoders.get('json')

    accept = request.META['HTTP_ACCEPT']
    for serializer in encoders.values():
        if serializer.can_emit(accept):
            # Serializer matched against the accept header; return it
            return serializer

    # Nothing can be matched; return nothing


def get_available():
    available = {}
    for name, item in encoders.items():
        available[name] = item.get_mimetype()

    return available


def find(request, **kwargs):
    """
    Determines the format to encode to and stores it upon success. Raises
    a proper exception if it cannot.
    """
    # Check locations where format may be defined in order of
    # precendence.
    if kwargs.get('format') is not None:
        # Format was provided through the URL via `.FORMAT`.
        encoder = encoders.get_by_name(kwargs['format'])

    else:
        # TODO: Should not have an else here and allow the header even
        # if the format check failed ?
        encoder = encoders.get_by_request(request)

    if encoder is None:
        # Failed to find an appropriate encoder
        # Get dictionary of available formats
        available = get_available()

        # TODO: No idea what to encode it with; using JSON for now
        # TODO: This should be a configurable property perhaps ?
        encoder = encoders.Json

        # encode the response using the appropriate exception
        raise exceptions.NotAcceptable(available)
