# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import Resource
from .meta import ResourceBase


__all__ = [
    'Resource'
]


class Resource(six.with_metaclass(ResourceBase, Resource)):
    """Implements the RESTful resource protocol for abstract resources.
    """
