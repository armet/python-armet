# -*- coding: utf-8 -*-
""" Defines code intended to be executed to facilitate the server operation.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division


def startup():
    """Executed at server startup to initialize the environment."""
    from django.contrib import admin

    # Discover administration modules
    admin.autodiscover()
