# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
from ..http import HttpResponse, constants


class Base(object):
    """Describes the base authentication protocol.
    """

    def __init__(self, require_active=True, **kwargs):
        """
        Initializes any configuration properties specific for this
        authentication protocol.
        """
        #! Whether to require users to have `is_active` flags in django set to
        #! `True`.
        self.require_active = require_active

    @abc.abstractmethod
    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None.

        @retval None           Unable to authenticate.
        @retval AnonymousUser  Able to authenticate but failed.
        @retval User           User object representing the curretn user.
        """
        pass

    def is_active(self, user):
        """Checks if the user is active; served as a point of extension."""
        return user.is_active if self.require_active else False

    @property
    def unauthenticated(self):
        """The response to return upon failing authentication."""
        return HttpResponse(status=constants.FORBIDDEN)
