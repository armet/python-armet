# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


__all__ = ['Request']


class Request(object):
    """Implements the RESTful request abstraction.
    """

    def header(self, name):
        """Retrieves a header with the passed name."""
        raise NotImplemented()

    @property
    def method(self):
        """Retrieves the method of the request.

        This must account for X-Http-Method-Override header, if set.
        """
        raise NotImplemented()
