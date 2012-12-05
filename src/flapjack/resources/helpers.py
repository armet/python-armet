# -*- coding: utf-8 -*-
"""Defines helpers for producing tuples used in configuring resources.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections


def field(path=None, collection=None):
    """Used in the `include` option to supply additional fields.

    @param[in] path
        Path on the resource object to return; if none is specified than there
        is no default value for this field (ie. unless a prepare_FOO method is
        declared it will always be `None`).

    @param[in] collection
        Whether the field is some kind of collection. This effects what is
        returned on `None` (null or []), etc.
    """
    return (path, collection)


#! Named tuple micro class for accessing relation information.
Relation = collections.namedtuple('Relation', (
    'resource', 'path', 'embed', 'local', 'related_name'
))

def relation(resource, path=None, embed=False, local=False, related_name=None):
    """Used in the `relations` option to relate fields with other resources."""
    return Relation(resource, path, embed, local, related_name)


#! Named tuple micro class for accessing parent information.
Parent = collections.namedtuple('Parent', (
    'resource', 'slug', 'name', 'related_name'
))

def parent(resource, slug, name, related_name):
    """Used in the resource class to ease parent assignment."""
    return Parent(resource, slug, name, related_name)
