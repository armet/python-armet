# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import six


__all__ = ['Response']


class Response(six.with_metaclass(abc.ABCMeta)):
    """Implements the RESTful response abstraction.
    """

    def __init__(self, status=None):
        if status is not None:
            self.status = status

    @abc.abstractproperty
    def status(self):
        """Gets the status code of the response."""

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""

    @abc.abstractproperty
    def content(self):
        """Gets the content of the response."""

    @content.setter
    def content(self, value):
        """Sets the content of the response."""

    @abc.abstractmethod
    def __getitem__(self, name):
        """Sets a header with the passed name."""

    @abc.abstractmethod
    def __setitem__(self, name, value):
        """Sets a header with the passed name."""
