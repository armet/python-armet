""" ..
"""
import json
import mimeparse


class Emitter(object):
    #! Applicable mimetypes for this emitter.
    mimetypes = []

    @classmethod
    def get_mimetype(cls):
        """Returns the preferred mimetype."""
        return cls.mimetypes[0] if cls.mimetypes else None

    @classmethod
    def can_emit(cls, accept_header):
        """
        Determine if this emitter can serialize an appropriate response to
        satisfy the ACCEPT header.
        """
        return mimeparse.best_match(cls.mimetypes, accept_header) != ''


class Json(Emitter):
    #! Applicable mimetypes for this emitter.
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
    def emit(cls, obj):
        if obj is not None:
            # Only emit something when we get something
            return json.dumps(obj)

        # Else; return nothing


# # TODO: JsonP
# class JsonP(Emitter):
#     #! Applicable mimetypes for this emitter.
#     mimetypes = [
#         # Official; this is 'just' javascript.
#         'text/javascript',

#         # Miscellaneous mimetypes that are used frequently (incorrectly).
#         'application/javascript',
#         'application/x-javascript',
#         'text/x-javascript',
#     ]

    # TODO: emit()...

# TODO: Find a more fun way to keep track of emitters
emitters = {
    'json': Json,
    # 'jsonp': JsonP
}


def get_by_name(format):
    return emitters.get(format.lower())


def get_by_request(request):
    if 'HTTP_ACCEPT' not in request.META:
        # No accept header provided; default to JSON
        return emitters.get('json')

    accept = request.META['HTTP_ACCEPT']
    for serializer in emitters.values():
        if serializer.can_emit(accept):
            # Serializer matched against the accept header; return it
            return serializer

    # Nothing can be matched; return nothing


def get_available():
    available = {}
    for name, item in emitters.items():
        available[name] = item.get_mimetype()

    return available
