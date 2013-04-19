# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
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
        # If the length of args is 1 and the first argument is a type
        # then this is being used without parens.
        if len(args) == 1 and isinstance(args[0], type):
            # Store no arguments and invoke ourself
            self.arguments = ()
            self(args[0])

        else:
            # Just store the arguments, we're being invoked with parenthesis.
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
