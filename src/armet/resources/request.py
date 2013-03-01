# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import six


__all__ = ['Request']


class Request(six.with_metaclass(abc.ABCMeta)):
    """Implements the RESTful request abstraction.
    """

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name."""

    @abc.abstractproperty
    def method(self):
        """Retrieves the method of the request.

        This must account for X-Http-Method-Override header, if set.
        """
