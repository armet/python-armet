"""Contains authorization stuff
"""


class Authorization(object):
    """
    Establishes the protocol for authorization; by default, all users are
    authorized.
    """

    def is_accessible(self, request, method):
        """Immediate authorization (eg, only admins may access a resource)."""
        return True

    def is_authorized(self, request, method, obj):
        """Authorization pass after the object has been constructed."""
        return True


class Model(Authorization):
    """
    Implements the authorization protocol using django model-based
    permissions.
    """

    # FIXME: Switch to use method names instead of http method names after
    #   refactor of the determine_method function is done.

    def is_accessible(self, request, method):
        """Immediate authorization (eg, only admins may access a resource)."""
        # if method == 'create':
        # if method == 'post':
        #     # Creating a new object; no object is neccessary.
        #     return request.user.has_perm('can_add')
        # ?
        return True

    def is_authorized(self, request, method, obj):
        """Authorization pass after the object has been constructed."""
        # if method == 'update':
        if method == 'put':
            # Updating; we should have an object.
            return request.user.has_perm('can_change', obj)

        if method == 'delete':
        # if method == 'destroy':
            # Destroying an existing object; check the perms.
            return request.user.has_perm('can_delete', obj)

        # Nothing interesting to check; reads, etc are filtered
        return True
