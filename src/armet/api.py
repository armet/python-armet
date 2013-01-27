# -*- coding: utf-8 -*-
"""Defines the api registry used to register and manage resources
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from collections import MutableSequence
from django.conf.urls import patterns, url, include
from armet import resources


class Api(resources.Resource, MutableSequence):
    """Implements an api registry used to make APIs visible.
    """

    # TODO: Implement the remainder of the methods.
    http_allowed_methods = ('GET',)

    # TODO: Implement the remainder of the operations.
    allowed_operations = ('read',)

    def __init__(self, name='api', *args, **kwargs):
        """
        Instantiates the registry and overrides the class resource name with
        what has been passed in.
        """
        if 'request' not in kwargs:
            # No request object just means we're being accessed as a registry;
            # tell it we don't care.
            kwargs['request'] = None

        # Let armet set us up.
        super(Api, self).__init__(*args, **kwargs)

        #! The name of the resource; overridden to be what is passed in.
        self.name = name

        #! The internal registry of resources.
        self._registry = kwargs.get('registry', [])

    def insert(self, index, resource):
        return self._registry.insert(index, resource)

    def __setitem__(self, key, value):
        self._registry[key] = value

    def __delitem__(self, key):
        del self._registry[key]

    def __getitem__(self, index):
        return self._registry[index]

    def __len__(self):
        return len(self._registry)

    def __iter__(self):
        return iter(self._registry)

    def __contains__(self, resource):
        return resource in self._registry

    @property
    def urls(self):
        """Returns a list of urls for all registered resources."""
        return patterns('',
            # URL expression for API browse.
            url(
                self._url_base_regex.format(self.name).format(''),
                self.view,
                # {'registry': self._registry},
                name=self.url_name,
                kwargs={'resource': self.name, 'registry': self._registry}),

            # URL includes for the resources in the registry.
            *[self._make_url(x) for x in self._registry]
        )

    def _make_url(self, resource):
        """Takes a resource class object and returns a corresponding url."""
        return url(r'^{}/'.format(self.name), include(resource.urls))

    def read(self):
        # There is no response; only links.
        return None
