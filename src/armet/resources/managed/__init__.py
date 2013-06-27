# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import ManagedResource as BaseManagedResource
from .meta import ManagedResourceBase

__all__ = [
    'ManagedResource'
]


class ManagedResource(
        six.with_metaclass(ManagedResourceBase, BaseManagedResource)):
    """Implements the RESTful resource protocol for managed resources.
    """
