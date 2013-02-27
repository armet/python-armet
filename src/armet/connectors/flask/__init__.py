# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


__all__ = [
    b'route',
]


def is_available(*capacities):
    """
    Detects if the environment is available for use in
    the (optionally) specified capacities.
    """
    try:
        # Attempted import
        import flask

        # TODO: Add additional checks to assert that flask is actually
        #   in use and available.

        # Detected connector.
        return True

    except ImportError:
        # Failed to import.
        return False


if is_available('http'):
    from .utils import route
