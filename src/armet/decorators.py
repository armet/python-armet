# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from .exceptions import ImproperlyConfigured


class route:
    """
    Mounts a resource on the passed URL mount point by invoking the
    `mount` classmethod.

    @example
        @route('/')
        class Resource(resources.Resource):
            # ...
    """

    def __init__(self, *args):
        # Store the arguments
        self.arguments = args

    def __call__(self, resource):
        # Ensure the resource has a `mount` classmethod.
        if not hasattr(resource, 'mount'):
            raise ImproperlyConfigured(
                'The {} resource doesn\'t have a `mount` method.'.format(
                resource.meta.name))

        # Hook up the resource at the mount point.
        resource.mount(*self.arguments)

        # Return the resource
        return resource
