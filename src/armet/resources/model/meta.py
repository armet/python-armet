# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from ..resource import meta
from . import options


class ModelResourceBase(meta.ResourceBase):

    options = options.ModelResourceOptions

    def __new__(cls, name, bases, attrs):
        # Construct the initial object.
        self = super(ModelResourceBase, cls).__new__(cls, name, bases, attrs)
        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return self
