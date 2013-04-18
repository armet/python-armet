# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import mimeparse
from . import utils


class Transcoder(object):

    #! Applicable mimetypes for this transcoder.
    mimetypes = ()

    @utils.classproperty
    def mimetype(cls):
        """Retrieves the 'default' mimetype."""
        return cls.mimetypes[0]

    @classmethod
    def can_transcode(cls, media_ranges):
        """Determine if this transcoder can encode or decode appropriately."""
        try:
            # Attempt to use mimeparse to determine if the mimetype matches
            return mimeparse.best_match(cls.mimetypes, media_ranges) != ''

        except ValueError:
            # Mimeparse died something fierce
            return False


class Form:
    """Multipart form data; as defined by HTML5.

    http://www.w3.org/TR/html5/constraints.html#multipart-form-data
    """
    mimetypes = ('multipart/form-data',)


class Url:
    """URL encoded form data; as defined by HTML5.

    http://www.w3.org/TR/html5/constraints.html#url-encoded-form-data
    """
    mimetypes = ('application/x-www-form-urlencoded',)


class Json:
    mimetypes = (
        # Offical; as per RFC 4627.
        'application/json',

        # Widely used (thanks <http://www.json.org/JSONRequest.html>.)
        'application/jsonrequest',

        # Miscellaneous mimetypes that are used frequently (incorrectly).
        'application/x-json',
        'text/json; charset=utf-8',

        # Widely used (incorrectly) thanks to ruby.
        'text/x-json; charset=utf-8',
    )


class Xml:
    mimetypes = (
        # To be used when the XML is NOT human-readable as per RFC 3023.
        # Our XML is not considered human-readable as it is minified before
        # transfer.
        'application/xml',

        # To be used when the XML is human-readable as per RFC 3023.
        'text/xml; charset=utf-8',
    )


class Text:
    """Sends and retrieves the textual representation of the URI.

    @warning
        This is only defined for scalar access. Arrays and objects will throw.
    """
    mimetypes = (
        # NOTE: This is not text/plain from HTML5.
        'text/plain; charset=utf-8',
    )


class Yaml:
    mimetypes = (
        # NOTE: No standardized mimetype as of yet.
        'application/x-yaml',
        'application/yaml',
        'text/yaml; charset=utf-8',
        'text/x-yaml; charset=utf-8',
    )


class Stream:
    """A pass-through transcoding for file transfer.

    @warning
        This is only defined for streams; all others will throw.
    """
    mimetypes = (
        'application/octect-stream',
    )


class MessagePack:
    """Messagepack data, see msgpack.org for more information.
    """
    mimetypes = (
        # NOTE: No standardized mimetype as of yet.
        'application/x-msgpack',
    )
