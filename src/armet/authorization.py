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

    def authorize(self, user, operation, resource, obj):
        """Determines authroization to a specific resource object.

        @param[in] user
            The user in question that is being checked.

        @param[in] operation
            The operation in question that is being performed (eg. 'read').

        @param[in] resource
            The resource instance that is being authorized.

        @param[in] obj
            The specific instance of an object returned by a `read` from
            the `resource`. This may also be an iterable of objects in which
            this method will filter out those that the user is not authorized
            for.

        @note
            This method may be called twice: once on the object
            being accessed (for 'read', 'update', and 'destroy'); as well as,
            on the updated object (for 'create' and 'update').

        @returns
            Returns the object or objects the user is authorized to access;
            or None, to indicate no authorization.
        """
        return obj


class ModelAuthorization(authorization.Authorization):
    """
    Implements the authorization protocol to use a django-based permission
    system linked with its ORM.
    """

    def __init__(self, permissions=None):
        """Initializes this and sets up the permission map.

        @param[in] permissions
            A map of operations to permissions to assert on an operation.
        """
        self.permissions = permissions
        if permissions is None:
            self.permissions = {
                'read':   ('read',)
                'create': ('add',),
                'update': ('change',),
                'destroy': ('delete',),
            }

    def has_perm(self, user, operation, obj=None):
        """
        Tests if the passed user has a permission for
        the passed operation on the optionally passed object.
        """
        try:
            # Lookup the permissions and do the permission checking.
            return user.has_perms(self.permissions[operation], obj)

        except KeyError:
            # Permission lookup failed, no specific permission for this method
            # Allow access.
            return True

    def is_accessible(self, user, operation, resource):
        return self.has_perm(user, operation)

    def is_authorized(self, user, operation, resource, obj):
        # Check for the appropriate permissions on the single object.
        return self.has_perm(user, operation, obj)

    def filter(self, user, operation, resource, iterable):
        try:
            # Filter out the iterable.
            return iterable.for_perms(user, self.permissions[operation])

        except KeyError:
            # Permission lookup failed. There are no specific permissions
            # associated with this request.
            return iterable

        except AttributeError:
            # Permission filtering method failed; fall back to a slower
            # has_perms check.
            return (self.has_perm(user, operation, x) for x in iterable)
