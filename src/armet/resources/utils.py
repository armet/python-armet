# -*- coding: utf-8 -*-
from armet.utils import classproperty


def connect(name):
    """Creates a proxy to a connector for a named attribute or method.
    """

    @property
    def proxy(self):
        for connector in self.connectors:
            data = vars(connector)
            if name in data:
                return data[name].__get__(self)

        raise AttributeError("class object '%s' has no attribute '%s'" % (
            type(self).__name__, name))

    return proxy


def classconnect(name):
    """Creates a proxy to a connector for a named attribute or classmethod.
    """

    @classproperty
    def proxy(cls):
        for connector in cls.connectors:
            data = vars(connector)
            if name in data:
                return data[name].__get__(cls)

        raise AttributeError("type object '%s' has no attribute '%s'" % (
            cls.__name__, name))

    return proxy
