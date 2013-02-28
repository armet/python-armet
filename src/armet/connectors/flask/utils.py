# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from flask import Flask
from armet.exceptions import ImproperlyConfigured


class route:
    """Mounts a resource on the passed url and flask application.

    @example
        @route(app, '/')
        class Resource(resources.Resource):
            # ...
    """

    def __init__(self, app, url='/'):
        # Store properites for later access.
        self.app = app
        self.url = url

        # Perform some minimal sanity checking.
        if not isinstance(app, Flask):
            raise ImproperlyConfigured(
                'Application must be a Flask application.')

    def __call__(self, resource):
        # Hook up the resource at the mount point.
        resource.mount(self.app, self.url)

        # Return the resource
        return resource
