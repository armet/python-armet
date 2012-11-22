# -*- coding: utf-8 -*-
"""Defines helpers for producing tuples used in configuring resources.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from .. import fields


def field(path=None, collection=False):
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
