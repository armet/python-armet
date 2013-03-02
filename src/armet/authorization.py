# -*- coding: utf-8 -*-
"""
Describes the authorization protocols and generalizations used to
authoirze access to a resource endpoint.
"""
from __future__ import print_function, unicode_literals, division


class Authorization(object):
    """
    Establishes the protocol for authorization; by default, all users are
    authorized.
    """

    #! A map of connectors that are required to use this authorization
    #! interface.
    # require = None

    def is_accessible(self, user, operation, resource):
        """
        Determines the accessibility to a resource endpoint for a particular
        operation. An inaccessible resource is indistinguishable from a
        non-existant resource.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @returns
            Returns true if the user can access the resource for
            the passed operation; otherwise, false.
        """
        return True

    def is_authorized(self, user, operation, resource, obj):
        """Determines authroization to a specific resource object.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @param[in] obj
            The specific instance of an object returned by a `read` from
            the `resource`.

        @note
            This method may be called twice: once on the object
            being accessed (for 'update', and 'destroy'); as well as,
            on the updated object (for 'create' and 'update').

        @returns
            Returns true to indicate authorization or false to indicate
            otherwise.
        """
        return True

    def filter(self, user, operation, resource, iterable):
        """
        Filters an iterable to return only the objects the user
        is authorized to access.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @param[in] iterable
            The iterable of objects to be checked.

        @returns
            Returns an iterable containing the remaining objects.
        """
        return iterable
