# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import importlib
from armet.utils import iter_modules


# Detect available connectors and merge their module __all__ with the
# globals for ease of access.
for module in iter_modules(importlib.import_module('armet.connectors')):
    if module.is_available():
        for key in getattr(module, '__all__', module.__dict__):
            globals()[key] = module.__dict__[key]
