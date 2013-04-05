# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from . import model, meta
from armet.utils.metaclass import make


__all__ = [
    'ModelResource'
]


class ModelResource(six.with_metaclass(
        make(meta.ModelResourceBase), model.ModelResource)):
    """Implements the RESTful resource protocol for model resources.
    """
