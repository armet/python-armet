# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


class classproperty(object):
    """Declares a read-only `property` that acts on the class object.
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(cls)


class boundmethod(object):
    """
    Declares a method that can be invoked as both an instance method
    and a class method.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, obj, cls):
        self.obj = obj if obj else cls
        return self

    def __call__(self, *args, **kwargs):
        return self.method(self.obj, *args, **kwargs)
