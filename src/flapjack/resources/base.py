# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six


class Options(object):
    """
    """

    def __init__(self, **kwargs):
        #! List of understood HTTP methods.
        self.http_method_names = kwargs.get('http_method_names', (
            'get',
            'post',
            'put',
            'delete',
            'patch',
            'options',
            'head',
            'connect',
            'trace',
        ))

        #! List of allowed HTTP methods.
        self.http_allowed_methods = kwargs.get('http_allowed_methods', (
            'get',
            'post',
            'put',
            'delete',
        ))

        #! List of allowed HTTP methods against a whole resource (eg /user).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_list_allowed_methods = kwargs.get(
            'http_list_allowed_methods', self.http_allowed_methods)

        #! List of allowed HTTP methods against a single resource (eg /user/1).
        #! If undeclared or None, will be defaulted to `http_allowed_methods`.
        self.http_detail_allowed_methods = kwargs.get(
            'http_detail_allowed_methods', self.http_allowed_methods)

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the differences
        #! between "PATCH and PUT", "PUT = create / update", etc.
        self.allowed_operations = kwargs.get('allowed_operations', (
            'read',
            'create',
            'update',
            'destroy',
        ))

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.list_allowed_operations = kwargs.get(
            'list_allowed_operations', self.allowed_operations)

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.detail_allowed_operations = kwargs.get(
            'detail_allowed_operations', self.allowed_operations)


class Meta(type):
    pass


class Resource(six.with_metaclass(Meta)):
    pass


__all__ = [
    Resource
]
