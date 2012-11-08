""" ..
"""
import mimeparse
from . import utils


class Transcoder(object):

    #! Registry of available transcoders.
    registry = None

    #! Applicable mimetypes for this transcoder.
    mimetypes = ()

    # @classmethod
    # def get(cls, mimetype):
    #     try:
    #         for transcoder in cls.registry.values():
    #             if transcoder.can_transcode(mimetype):
    #                 # Transcoder matched against the mimetype; return it
    #                 return transcoder

    #     except:
    #         # Mimetype is so badly formatted mimeparse died; return nothing
    #         pass

    #     # Nothing can be matched; return nothing

    @utils.classproperty
    def mimetype(cls):
        # Return the 'default' mimetype.
        return cls.mimetypes[0]

    @classmethod
    def can_transcode(cls, media_ranges):
        """Determine if this transcoder can encode or decode appropriately."""
        try:
            # Attempt to use mimeparse to determine if the mimetype matches
            return mimeparse.best_match(cls.mimetypes, media_ranges) != ''

        except:
            # Mimeparse died something fierce
            return False


class Bin:

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        'application/octect-stream',
    )


class Form:

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        'multipart/form-data',
    )


class Url:

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        'application/x-www-form-urlencoded',
    )


class Json:

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


class Text:

    #! Applicable mimetypes for this transcoder.
    mimetypes = 'text/plain',


class JsonP:

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        # Official; this is 'just' javascript.
        'text/javascript',

        # Miscellaneous mimetypes that are used frequently (incorrectly).
        'application/javascript',
        'application/x-javascript',
        'text/x-javascript',
    )
