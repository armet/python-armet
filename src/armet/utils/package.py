# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import importlib


def import_module(name):
    """Attempt to import a module; returns None if unsuccessful."""
    try:
        return importlib.import_module(name)

    except ImportError:
        return None
