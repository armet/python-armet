# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from . import base


class Options(base.Options):
    pass


class Meta(base.Meta):
    pass


class Model(six.with_metaclass(base.Resource, Meta)):
    pass


__all__ = [
    Model
]
