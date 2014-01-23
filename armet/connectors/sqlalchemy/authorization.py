# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.authorization import ManagedAuthorization
from armet.exceptions import ImproperlyConfigured


try:
    import shield
    from shield.contrib.sqlalchemy import evaluate

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
        expr = shield.has(
            *self.permissions[operation], bearer=user, target=item)
        return evaluate(expr, item)

    def filter(self, user, operation, resource, iterable):
        expr = shield.filter(
            *self.permissions[operation],
            bearer=user, target=resource.meta.model)

        clause = evaluate(expr, resource.meta.model)
        return resource.filter(clause, iterable)
