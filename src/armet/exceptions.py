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


class ValidationError(BaseException):
    """
    Something has been found invalid during the attribute clean cycle;
    normally resulting from form or some type of validation.
    """

    def __init__(self, *errors):
        self.errors = errors
