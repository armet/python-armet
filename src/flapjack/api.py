# -*- coding: utf-8 -*-
"""Defines the api registry used to register and manage resources
"""
from django.conf.urls import patterns, url, include
from flapjack import resources


class Api(resources.Resource):
    """An api registry used to wrangle apis
    """

    allowed_operations = ('read')

    def __init__(self, api_name="v0"):
        # set the api name
        self.name = api_name
        self._registry = []

    def register(self, resource):
        """take a class object as a parameter.
        add the resource to a registry.
        """
        self._registry.append(resource)

    def unregister(self, resource):
        """delete from registry
        """
        self._registry.remove(resource)

    @property
    def urls(self):
        """Returns a url list of all resources registered with this resource
        """
        return patterns('', [self.urlify(x) for x in self._registry])

    def urlify(self, resource):
        """Takes a resource list returns a corresponding url object
        """
        return url(r'{}/'.format(self.name), include(resource.urls))

    def __setitem__(self, key, value):
        """Implement a Sequence method
        """
        self._registry[key] = value

    def __delitem__(self, key):
        """Implement a sequence method
        """
        del self._registry[key]

    def insert(self, key, item):
        """Implement a sequence method
        """
        self._registry.insert(key, item)

    def __getitem__(self, index):
        """Implement a sequence method
        """
        return self._registry[index]

    def __len__(self):
        """Implement a sequence method
        """
        return len(self._registry)

    def __iter__(self):
        """Implement a sequence method
        """
        return self._registry

    def __contains__(self, item):
        """Implement a conditional method
        """
        return item in self._registry
