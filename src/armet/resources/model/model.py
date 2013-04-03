# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
import collections
import re
import logging
from armet import http
from armet.http import exceptions
from ..resource import base


logger = logging.getLogger(__name__)


class ModelResource(base.Resource):
    """Implements the RESTful resource protocol for model-bound resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.ModelResource` (defined in
        the `__init__.py`).
    """
