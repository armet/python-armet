# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


class Resource(object):
    """Implements the RESTful resource protocol for abstract resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    def __init__(self, **kwargs):
        """Initializes the resources and sets its properites."""
        pass

    def dispatch(self):
        return self.meta.name
