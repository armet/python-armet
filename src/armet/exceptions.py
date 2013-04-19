# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


class ImproperlyConfigured(BaseException):
    """Something has been set up or configured incorrectly.
    """


class InvalidOperation(BaseException):
    """
    Something is being asked to operate outside of the defined specification
    of it operating.
    """
