# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import importlib


__all__ = [
]


def is_available(*capacities):
    """
    Detects if the environment is available for use in
    the (optionally) specified capacities.
    """
    try:
        # Attempted import.
        importlib.import_module('django')

    except ImportError:
        # Failed to import django
        return False

    # Import the exception we might get
    from django.core.exceptions import ImproperlyConfigured

    try:
        # Now try and use it.
        conf = importlib.import_module('django.conf')
        conf.settings.DEBUG

        # Detected connector.
        return True

    except ImproperlyConfigured:
        # We don't have an available settings file; django is actually in use.
        return False
