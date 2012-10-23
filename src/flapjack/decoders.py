""" ..
"""
import abc
import mimeparse
import json
from . import exceptions


class Decoder(object):
    #! Applicable mimetypes for this Decoder
    mimetypes = []

    @classmethod
    def can_parse(cls, content_type_header):
        """
        Determine if this decoder can deserialize an appropriate message
        specified by the CONTENT-TYPE header.
        """
        return mimeparse.best_match(cls.mimetypes, content_type_header) != ''

    @classmethod
    @abc.abstractmethod
    def decode(cls, request):
        """
        Constructs an object dictionary from the request body according to the
        media-type specified in the `Content-Type` header.

        @param[in] request
            Django request object containing the request body (at a minimum:
            body, POST, and FILES).

        @returns
            A dictionary containing the parameters of the request.
        """
        pass


class Form(Decoder):
    #! Applicable mimetypes for this decoder
    mimetypes = [
        'multipart/form-data',
        'application/x-www-form-urlencoded',
    ]

    @classmethod
    def decode(cls, request):
        # Build the initial object as a copy of the POST data
        obj = request.POST

        # Iterate through this absurd multi-value-dict and multiplex the
        # values into obj
        for name in request.FILES:
            if name not in obj:
                obj[name] = []

            obj[name].extend(request.FILES.getlist(name))

        # Now flatten those in that can be flattened
        for name, item in obj.items():
            if len(item) == 1:
                obj[name] = item[0]

        # Return the final object dictionary
        return obj


class Json(Decoder):

    #! Mimetypes for this decoder.  Very similar to the encoders
    mimetypes = [
        'application/json',
        'application/jsonrequest',
        'application/x-json',
        'text/json',
        'text/x-json',
    ]

    @classmethod
    def parse(cls, request):
        return json.loads(request.body)


# TODO: Find a more fun way to keep track of Decoders
decoders = [
    Json,
    Form,
]


def get(request):
    if 'CONTENT_TYPE' not in request.META:
        # No accept header provided; we can do nothing as the default
        # is application/octet-stream.
        # TODO: Perhaps devise a way to accept this ?
        return None

    content_type = request.META['CONTENT_TYPE']
    for Decoder in decoders:
        if Decoder.can_parse(content_type):
            # Decoder matched against the type header; return it
            return Decoder

    # Nothing can be matched; return nothing


def find(request, **kwargs):
    """
    Determines the format to decode to and stores it upon success. Raises
    a proper exception if it cannot.
    """
    decoder = get(request)
    if decoder is None:
        # Failed to find an appropriate decoder; we have no idea how to
        # handle the data.
        raise exceptions.UnsupportedMediaType()
    return decoder
