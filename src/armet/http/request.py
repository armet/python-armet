# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import collections


__all__ = ['Request']


#
class Request(collections.Mapping):
    """Implements the RESTful request abstraction.
    """

    def __hash__(self):
        """This class inherits from collections.Mapping, which means it gains
        all the properties of a dict, including the inability to hash it.
        Memoization involves stuffing the class instance inside of a dictionary
        along with the method's return values. This means that instances of
        this class need to be hashable in order to exist inside a dict."""
        return id(self)

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name."""

    @abc.abstractmethod
    def __len__(self, name):
        """Retrieves the number of headers in this request."""

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterable for all headers in this request."""

    @abc.abstractproperty
    def method(self):
        """Retrieves the method of the request.

        This must account for X-Http-Method-Override header, if set.
        """

    def __contains__(self, name):
        try:
            self[name]
        except KeyError:
            return False
        return True
