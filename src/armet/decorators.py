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
        # Just store the arguments.
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


def asynchronous(resource):
    """Instructs a decorated resource that it is to be asynchronous.

    An asynchronous resource means that `response.close()` must be called
    explicitly as returning from a method (eg. `get`) does not close
    the connection.

    @note
        This can also be configured by setting `asynchronous` to `True`
        on `<resource>.Meta`. The benefit of the decorator is that this
        can be applied to specific methods as well as the entire class
        body.
    """
    # TODO: Check for gevent support...

    # Flip the asynchronous switch.
    resource.meta.asynchronous = True

    # Return the resource
    return resource
