"""Contains authorization stuff
"""

class Authorization(object):
    """
    Establishes the protocol for authorization; by default, all users are
    authorized.
    """

    def __init__(self, perms, resource_perms=None, obj_perms=None):
        """Takes the permissions lookup to look in filtering.
        `perms` are used in both hashes and are overridden by anything in
        `resource_perms` and `obj_perms` for their respective perm types
        """
        # clone the perms dict incase someone is using it
        self.resource_perms, self.obj_perms = dict(perms), dict(perms)

        if resource_perms is not None:
            self.resource_perms.update(resource_perms)
        if obj_perms is not None:
            self.obj_perms.update(obj_perms)

    def is_accessible(self, request, method):
        """Immediate authorization (eg, only admins may access a resource)."""
        return True

    def is_authorized(self, request, method, obj):
        """Authorization pass after the object has been constructed."""
        return True

    def filter(self, request, method, iterable):
        """Filter pass to remove items that the user is not authorized
        to access.
        """
        return iterable


class Resource(Authorization):
    """Implements resource based authorization
    """

    def is_accessible(self, request, method):
        """Immediate authorization (eg, only admins may access a resource)."""
        return self.try_perm(request, self.resource_perms, method)

    @staticmethod
    def try_perm(request, resource, method, obj=None):
        """Simple permission checking for singular objects
        """
        try:
            # Lookup the permission type
            permission = resource[method]

            # Do the permission checking
            return request.user.has_perms(permission, obj)

        except KeyError:
            # Permission lookup failed, no specific permission for this method
            # Allow access.
            return True


class Model(Resource):
    """
    Implements the authorization protocol using django model-based
    permissions.
    """

    # FIXME: Switch to use method names instead of http method names after
    #   refactor of the determine_method function is done.

    # Inherits is_accessible from Resource

    def is_authorized(self, request, method, obj):
        """Authorization pass after the object has been constructed."""
        return self.try_perm(request, self.obj_perms, method, obj)

    def filter(self, request, method, iterable):
        """Filter pass to remove items that the user is not authorized
        to access.
        """
        try:
            # Lookup permissions for this object
            permission = self.obj_perms[method]

            # Return iterable for this
            return iterable.for_perms(request.user, permission)

        except KeyError:
            # Permission lookup failed.  there are no specific permissions
            # associated with this request.  just return it
            return iterable

        except AttributeError:
            # for_perm invocation failed, fall back to slower has_perm method
            return (request.user.has_perm(permission, x) for x in iterable)
