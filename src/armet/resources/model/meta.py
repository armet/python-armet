# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from ..resource import meta
from . import options


class ModelResourceBase(meta.ResourceBase):

    options = options.ModelResourceOptions
