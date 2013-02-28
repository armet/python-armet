# -*- coding: utf-8 -*-
"""Defines the RESTful resource protocol for resources.
"""
from __future__ import print_function, unicode_literals, division
import six
from armet.resources import base, meta
from armet.resources.request import Request
from armet.resources.response import Response


class Resource(six.with_metaclass(meta.ResourceBase, base.Resource)):
    """Implements the RESTful resource protocol for abstract resources.
    """
