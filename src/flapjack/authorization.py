"""Contains authorization stuff
"""


class Authorization(object):
    """
    Establishes the protocol for authorization; by default, all users are
    authorized.
    """

    def __init__(self):
        pass

    def is_accessible(self, request, identifier):
        """Immediate authorization (eg, only admins may access a resource)."""
        return True

    def is_authorized(self, obj):
        """Authorization pass after the object has been constructed."""
        return True

    # def limit_queries(self, query):
    #     """Apply query limits to the result list
    #     """
    #     return query


class Model(Authorization):
    """
    Implements the authorization protocol using django model-based
    permissions.
    """

    def __init__(self):
        pass

    def is_accessible(self, request, method):
        """Immediate authorization (eg, only admins may access a resource)."""
        if method == 'create':
            # Creating a new object; no object is neccessary
            return self.request.user.has_perm('can_add')
        # ?
        return True

    def is_authorized(self, request, identifier, method, obj):
        """Authorization pass after the object has been constructed."""
        if method == 'update':
            # Updating; we should have an object
            return self.request.user.has_perm('can_change', obj)

        if method == 'destroy':
            # Destroying an existing object; check the perms
            return self.request.user.has_perm('can_delete', obj)

        # Nothing interesting to check; reads, etc are filtered
        return True

    # def is_authorized(self, request, obj=None):
    #     """Checks if the user is authorized to do the requested action."""
    #     # GET-style methods are always allowed.
    #     if request.method in ('GET', 'OPTIONS', 'HEAD'):
    #         return True

    #     klass = self.resource_meta.object_class

    #     # If it doesn't look like a model, we can't check permissions.
    #     if not klass or not getattr(klass, '_meta', None):
    #         return True

    #     permission_map = {
    #         'POST': ['can_add'],
    #         'PUT': ['can_change'],
    #         'DELETE': ['can_delete'],
    #         'PATCH': ['can_add', 'can_change', 'can_delete'],
    #     }

    #     # If we don't recognize the HTTP method, we don't know what
    #     # permissions to check. Deny.
    #     if request.method not in permission_map:
    #         return False

    #     # User must be logged in to check permissions.
    #     if not hasattr(request, 'user'):
    #         return False

    #     return request.user.has_perms(permission_map[request.method], obj)
