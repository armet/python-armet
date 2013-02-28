# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re
import logging


logger = logging.getLogger(__name__)


class Resource(object):
    """Implements the RESTful resource protocol for abstract resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    @classmethod
    def redirect(cls, path):
        """Redirect to the canonical URI for this resource.

        @note
            This method does not know how to complete the operation and
            leaves that to an implementation class in a connector. The result
            is the URI to redirect to.
        """
        if cls.meta.trailing_slash:
            path += '/'
        else:
            del path[-1]
        return path

    @classmethod
    def view(cls, path):
        """
        Entry-point of the request cycle; Handles resource creation
        and delegation.

        @param[in] path
            The path accessor for the resource (eg. for a request like
            GET /api/resource/foo/bar/1/4 if resource is mounted on /api/ then
            path will be '/bar/1/4/'
        """
        try:
            # Parse any arguments out of the path.
            arguments = cls.parse(path)

            # Traverse down the path and determine to resource we're actually
            # accessing.
            resource = cls.traverse(arguments)

            # Instantiate the resource.
            obj = resource(**arguments)

            # Initiate the dispatch cycle and return its response.
            response = obj.dispatch()

            # TODO: Commit

            # Return the response from the dispatch cycle.
            return response

        except BaseException as ex:
            # Something unexpected happenend.
            # TODO: Rollback

            # Log error message to the logger.
            logger.exception('Internal server error')

            # Return nothing and indicate a server failure.
            # TODO: Pass back the status code (500).
            return None

    #! Precompiled regular expression used to parse out the path.
    _parse_pattern = re.compile(
        r'^(?:\:(?P<query>[^/]+?))?'
        r'(?:\:)?'
        r'(?:/(?P<slug>[^/]+?))?'
        r'(?:/(?P<path>.+?))??'
        r'(?:\.(?P<extension>[^/]+?))??$')

    @classmethod
    def parse(cls, path):
        """Parses out parameters and separates them out of the path."""
        return re.match(cls._parse_pattern, path or '').groupdict()

    @classmethod
    def traverse(cls, arguments):
        """Traverses down the path and determines the accessed resource."""
        return cls

    def __init__(self, **kwargs):
        """Initializes the resources and sets its properites."""
        print(kwargs)

    def dispatch(self):
        """Entry-point of the dispatch cycle for this resource."""
        return self.meta.name
