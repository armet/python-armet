# -*- coding: utf-8 -*-
"""Tuples of the accepted media types for the various supported content types.

The first media type of each respective listing is what armet will
provide for its `Content-Type` upon serialization; armet will accept
any of the listed types when receiving content or when asked to
serialize in a specific format.
"""
from __future__ import absolute_import, unicode_literals, division

#! Multipart form data; as defined by HTML5.
#!
#! http://www.w3.org/TR/html5/constraints.html#multipart-form-data
FORM_DATA = 'multipart/form-data',

#! URL encoded form data; as defined by HTML5.
#!
#! http://www.w3.org/TR/html5/constraints.html#url-encoded-form-data
URL = 'application/x-www-form-urlencoded',

#! JavaScript Object Notation, is a text-based open standard designed
#! for human-readable data interchange.
JSON = (
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

#! Extensible Markup Language (XML) is a markup language that defines a set
#! of rules for encoding documents in a format that is both human-readable
#! and machine-readable.
XML = (
    # To be used when the XML is NOT human-readable as per RFC 3023.
    # Our XML is not considered human-readable as it is minified before
    # transfer.
    'application/xml',

    # To be used when the XML is human-readable as per RFC 3023.
    'text/xml; charset=utf-8',
)

#! YAML is a human friendly data serialization standard
#! for all programming languages.
#!
#! @note
#!      There is no standard media type for YAML.
YAML = (
    'application/x-yaml',
    'application/yaml',
    'text/yaml; charset=utf-8',
    'text/x-yaml; charset=utf-8',
)
