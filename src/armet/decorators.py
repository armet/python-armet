# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .exceptions import ImproperlyConfigured
import six
from . import utils


class route:
    """
    Mounts a resource on the passed URL mount point by invoking the
    `mount` classmethod.

    @example
        @route('/')
        class Resource(resources.Resource):
            # ...
    """

    def __init__(self, *args, **kwargs):
        # Just store the arguments.
        self.args = args
        self.kwargs = kwargs

    def __call__(self, resource):
        # Is the resources a function?
        if callable(resource) and not isinstance(resource, type):
            # Yes; call the resource decorator.
            import armet
            resource = armet.resource(**self.kwargs)(resource)

        # Ensure the resource has a `mount` classmethod.
        if not hasattr(resource, 'mount'):
            raise ImproperlyConfigured(
                'The {} resource doesn\'t have a `mount` method.'.format(
                    resource.meta.name))

        # Hook up the resource at the mount point.
        resource.mount(*self.args)

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


#! Mapping of lightweight resources.
_resources = {}

#! Mapping of functional handlers for the lightweight resources.
_handlers = {}


def resource(**kwargs):
    """Wraps the decorated function in a lightweight resource."""
    def inner(function):
        name = kwargs.pop('name', None)
        if name is None:
            name = utils.dasherize(function.__name__)

        methods = kwargs.pop('methods', None)
        if isinstance(methods, six.string_types):
            # Tuple-ify the method if we got just a string.
            methods = methods,

        # Construct a handler.
        handler = (function, methods)

        if name not in _resources:
            # Initiate the handlers list.
            _handlers[name] = []

            # Construct a light-weight resource using the passed kwargs
            # as the arguments for the meta.
            from armet import resources
            kwargs['name'] = name

            class LightweightResource(resources.Resource):
                Meta = type(str('Meta'), (), kwargs)

                def route(self, request, response):
                    for handler, methods in _handlers[name]:
                        if methods is None or request.method in methods:
                            return handler(request, response)

                    resources.Resource.route(self)

            # Construct and add this resource.
            _resources[name] = LightweightResource

        # Add this to the handlers.
        _handlers[name].append(handler)

        # Return the resource.
        return _resources[name]

    # Return the inner method.
    return inner
