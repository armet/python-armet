""" ..
"""
import mimeparse
from . import utils


class Transcoder(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = ()

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

class Xml(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = (
        #  RFC 3023: application/xml to be used when the XML is NOT human-readable.
        'application/xml',
        #  RFC 3023: text/xml to be used when the XML is human-readable.
        'text/xml',


    )


class Text:

    #! Applicable mimetypes for this transcoder.
    mimetypes = 'text/plain',
