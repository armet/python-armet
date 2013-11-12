# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .resource import Resource
from .managed import ManagedResource
from .model import ModelResource

__all__ = [
    'Resource',
    'ManagedResource',
    'ModelResource'
]
