# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import os
import pkgutil
import importlib


def import_module(name):
    """Attempt to import a module; returns None if unsuccessful."""
    try:
        return importlib.import_module(name)

    except ImportError:
        return None

def iter_modules(package):
    """Iterate through all modules of a packge."""
    prefix = package.__name__
    path = os.path.dirname(package.__file__)
    for _, name, _ in pkgutil.iter_modules([path]):
        yield import_module('{}.{}'.format(prefix, name))
