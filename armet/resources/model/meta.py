# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ..managed import meta
from . import options


class ModelResourceBase(meta.ManagedResourceBase):

    options = options.ModelResourceOptions

    connectors = ['http', 'model']
