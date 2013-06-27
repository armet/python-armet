# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import ModelResource as BaseModelResource
from .meta import ModelResourceBase

__all__ = [
    'ModelResource'
]


class ModelResource(six.with_metaclass(ModelResourceBase, BaseModelResource)):
    """Implements the RESTful resource protocol for model resources.
    """
