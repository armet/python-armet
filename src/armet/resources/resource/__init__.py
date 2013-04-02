# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from . import base, meta


__all__ = [
    'Resource'
]


class Resource(six.with_metaclass(meta.ResourceBase, base.Resource)):
    """Implements the RESTful resource protocol for abstract resources.
    """
