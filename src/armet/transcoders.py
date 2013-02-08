# -*- coding: utf-8 -*-
"""Collection of registered mimetypes for encoders and decoders.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
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


class Binary:
    mimetypes = (
        # Intended to literally mean 'binary' data; as in, a pass-through
        # encoding.
        'application/octect-stream',
    )


class Form:
    mimetypes = (
        # Multipart form data; as defined by HTML5.
        # <http://www.w3.org/TR/html5/constraints.html#multipart-form-data>
        'multipart/form-data',
    )


class Url:
    mimetypes = (
        # URL encoded form data; as defined by HTML5.
        # <http://www.w3.org/TR/html5/constraints.html#url-encoded-form-data>
        'application/x-www-form-urlencoded',
    )


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
    mimetypes = (
        # Meant to be used to retrieve individual attributes from a resource.
        # NOTE: This is not text/plain from HTML5. When used on individual
        #   attributes this is a pass through and when used on whole resources
        #   it is stylized and resembles YAML.
        'text/plain; charset=utf-8',
    )


class Yaml:
    mimetypes = (
        # Not too sure on what the official one is as of yet.
        'application/x-yaml',
        'application/yaml',
        'text/yaml; charset=utf-8',
        'text/x-yaml; charset=utf-8',
    )
