""" ..
"""
import six
import mimeparse
from django.core.exceptions import ImproperlyConfigured


class DeclarativeTranscoder(type):

    def __init__(cls, name, bases, attributes):
        # Instantiate a fresh registry for this class object
        cls.registry = {}

        # Delegate to python magic to initialize the class object
        super(DeclarativeTranscoder, cls).__init__(name, bases, attributes)

    @property
    def mimetype(cls):
        # Return the 'default' mimetype.
        return cls.mimetypes[0]


class Transcoder(six.with_metaclass(DeclarativeTranscoder)):

    #! Registry of available transcoders.
    registry = None

    #! Applicable mimetypes for this transcoder.
    mimetypes = ()

    @classmethod
    def get(cls, mimetype):
        for transcoder in cls.registry.values():
            if transcoder.can_transcode(mimetype):
                # Transcoder matched against the mimetype; return it
                return transcoder

        # Nothing can be matched; return nothing

    @classmethod
    def register(cls, **kwargs):
        def constructor(ctor):
            # Default name to the lowercase'd class name.
            name = kwargs.get('name', ctor.__name__.lower())

            if name not in cls.registry:
                # Record the class object in the registry.
                cls.registry[name] = ctor

            else:
                # We already have one of these registered; die.
                raise ImproperlyConfigured(
                    'An encoder or decoder has already been registered as '
                    '`{}`.'.format(name))

            return ctor
        return constructor

    @classmethod
    def can_transcode(cls, media_ranges):
        """Determine if this transcoder can encode or decode appropriately."""
        try:
            # Attempt to use mimeparse to determine if the mimetype matches
            return mimeparse.best_match(cls.mimetypes, media_ranges) != ''
        except:
            # Mimetype is so badly formatted mimeparse died
            return False


class Form(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        'multipart/form-data',
    )


class Url(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        'application/x-www-form-urlencoded',
    )


class Json(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        # Offical; as per RFC 4627.
        'application/json',

        # Widely used (thanks <http://www.json.org/JSONRequest.html>.)
        'application/jsonrequest',

        # Miscellaneous mimetypes that are used frequently (incorrectly).
        'application/x-json',
        'text/json',

        # Widely used (incorrectly) thanks to ruby.
        'text/x-json',
    )


class Text(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = 'text/plain',


# # TODO: JsonP
# class JsonP(object):
#
#     # ! Applicable mimetypes for this transcoder.
#     mimetypes = (
#         # Official; this is 'just' javascript.
#         'text/javascript',

#         # Miscellaneous mimetypes that are used frequently (incorrectly).
#         'application/javascript',
#         'application/x-javascript',
#         'text/x-javascript',
#     )
