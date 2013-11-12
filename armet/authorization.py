# -*- coding: utf-8 -*-
"""
Describes the authorization protocols and generalizations used to
authorize access to a resource endpoint.
"""
from __future__ import absolute_import, unicode_literals, division
from armet.exceptions import ImproperlyConfigured
from armet import http


class Authorization(object):
    """
    Establishes the protocol for authorization; by default, all users are
    authorized.
    """

    def is_accessible(self, user, method, resource):
        """
        Determines the accessibility to a resource endpoint for a particular
        method. An inaccessible resource is indistinguishable from a
        non-existant resource.

        @param[in] user
            The user in question that is being checked.

        @param[in] method
            The method in question that is being performed (eg. 'GET').

        @param[in] resource
            The resource instance that is being authorized.

        @returns
            Returns true if the user can access the resource for
            the passed operation; otherwise, false.
        """
        return True

    def inaccessible(self):
        """Informs the client that the resource is inaccessible."""
        raise http.exceptions.Forbidden()

    def is_authorized(self, user, operation, resource, item):
        """Determines authroization to a specific resource object.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @param[in] item
            The specific instance of an object returned by a `read` from
            the `resource`.

        @returns
            Returns true to indicate authorization or false to indicate
            otherwise.
        """
        return True

    def unauthorized(self):
        """Informs the client that it is not authrozied for the resource."""
        raise http.exceptions.Forbidden()

    def filter(self, user, operation, resource, iterable):
        """
        Filters an iterable to contain only the items for which the user
        is authorized to perform the operation on.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @param[in] iterable
            The iterable of objects to be checked. This method is called
            from the model connector so the actual value of this parameter
            depends on the model connector (eg. it may be a django queryset).

        @returns
            Returns an iterable containing the remaining objects.
        """
        return iterable


class ManagedAuthorization(Authorization):
    """Extends the authorization protocol to apply to managed resources.

    Managed resources only check accessibility and authorization based on
    the operation (eg. 'read') and not the method (eg. 'GET').
    """

    def inaccessible(self):
        """Informs the client that the resource is inaccessible."""
        raise http.exceptions.NotFound()


try:
    import shield

except ImportError:
    shield = None


class ShieldAuthorization(ManagedAuthorization):
    """Implements managed authorization using the shield permissions framework.
    """

    def __init__(self, permissions=None):
        # Ensure we have access to the shield framework.
        if shield is None:
            raise ImproperlyConfigured(
                "'shield' is required to use 'ShieldAuthorization'")

        #! Permissions to check for each operation.
        self.permissions = permissions
        if self.permissions is None:
            self.permissions = {
                'read': ('read',),
                'create': ('create',),
                'update': ('update',),
                'destroy': ('destroy',)
            }

    def is_authorized(self, user, operation, resource, item):
        return shield.has(
            *self.permissions[operation], bearer=user, target=item)

    def filter(self, user, operation, resource, iterable):
        clause = shield.filter(
            *self.permissions[operation],
            bearer=user, target=resource.meta.model)

        return resource.filter(clause, iterable)
