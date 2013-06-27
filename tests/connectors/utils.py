# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from importlib import import_module


def force_import_module(name):
    if name in sys.modules:
        return reload(sys.modules[name])

    else:
        return import_module(name)
