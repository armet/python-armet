# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .decorators import classproperty, boundmethod
from .functional import cons, compose
from .string import dasherize
from .package import import_module

__all__ = [
    'classproperty',
    'boundmethod',
    'cons',
    'compose',
    'import_module',
    'dasherize',
    'super'
]


class Superclass(object):

    def __init__(self, instance, cls, mro, index):
        self._index = index
        self._instance = instance
        self._cls = cls
        self._mro = mro

    def __getattr__(self, name):
        index = self._index
        while index < len(self._mro):
            cls = self._mro[index]
            if name in cls.__dict__:
                return cls.__dict__[name].__get__(self._instance, self._cls)

            index += 1


def super(current, obj):
    if isinstance(obj, type):
        # Get the MRO for the passed object.
        mro = obj.__mro__

        # Resolve an instance and class object from the object.
        cls, self = obj, None

    else:
        # Get the MRO for the passed object.
        mro = type(obj).__mro__

        # Resolve an instance and class object from the object.
        cls, self = type(obj), obj

    # Resolve the superclass.
    return Superclass(obj, cls, mro, mro.index(current) + 1)
