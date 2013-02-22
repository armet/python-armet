# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


class Resource(object):
    """Implements the RESTful resource protocol for abstract resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    @classmethod
    def view(cls, path):
        """
        Entry-point of the request cycle; Handles resource creation
        and delegation.

        @param[in] path
            The path accessor for the resource (eg. for a request like
            GET /api/resource/foo/bar/1/4 if resource is mounted on /api/ then
            path will be 'bar/1/4'
        """
        pass

    @staticmethod
    def parse(path):
        """Parses out parameters and separates them out of the path."""
        pass

    def __init__(self, **kwargs):
        """Initializes the resources and sets its properites."""
        pass

    def dispatch(self):
        """Entry-point of the dispatch cycle for this resource."""
        return self.meta.name
