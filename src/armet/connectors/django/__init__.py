# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


__all__ = [
]


def is_available(*capacities):
    """
    Detects if the environment is available for use in
    the (optionally) specified capacities.
    """
    try:
        # Attempted import.
        import django

        # Now try and use it.
        from django.conf import settings
        settings.DEBUG

        # Detected connector.
        return True

    except ImportError:
        # Failed to import django; or, we don't have a proper settings
        # file.
        return False
