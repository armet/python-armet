# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import authorization


class ModelAuthorization(authorization.Authorization):
    """
    Implements the authorization protocol to use a django-based permission
    system linked with its ORM.
    """

    # require = {
    #     'http': 'armet.connectors.django'
    #     'database': 'armet.connectors.django'
    # }

    def __init__(self, permissions=None):
        """Initializes this and sets up the permission map.

        @param[in] permissions
            A map of operations to permissions to assert on an operation.
        """
        self.permissions = permissions
        if permissions is None:
            self.permissions = {
                'read':   ('read',),
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
