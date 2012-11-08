# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from .base import Resource, Meta


class Meta(Meta):
    pass


class Resource(six.with_metaclass(Meta, Resource)):
    pass
