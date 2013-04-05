# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from ..resource import meta
from . import options


class ModelResourceBase(meta.ResourceBase):

    options = options.ModelResourceOptions
