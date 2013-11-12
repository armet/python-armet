# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from six.moves import reload_module
from importlib import import_module


def force_import_module(name):
    if name in sys.modules:
        return reload_module(sys.modules[name])

    else:
        return import_module(name)


def unload_module(name):
    if name in sys.modules:
        del sys.modules[name]
