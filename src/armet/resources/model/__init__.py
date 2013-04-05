# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from .model import ModelResource
from .meta import ModelResourceBase


__all__ = [
    'ModelResource'
]


class ModelResource(six.with_metaclass(ModelResourceBase, ModelResource)):
    """Implements the RESTful resource protocol for model resources.
    """
