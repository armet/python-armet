# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from . import base, meta
from armet.utils.metaclass import make


__all__ = [
    'Resource'
]


class Resource(six.with_metaclass(make(meta.ResourceBase), base.Resource)):
    """Implements the RESTful resource protocol for abstract resources.
    """
