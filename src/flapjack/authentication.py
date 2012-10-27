"""Contains authentication stuff
"""
from .http import HttpResponse, constants
from django.contrib.auth import authenticate


class Authentication(object):
    """
    Establishes the protocol for authentication; by default, all users are
    authenticated.
    """

    def __init__(self, require_active=True, **kwargs):
        #! Whether to require users to have `is_active` flags in django set to
        #! `True`.
        self.require_active = require_active

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None."""
        return None

    def is_active(self, user):
        """Checks if the user is active; served as a point of extension."""
        return user.is_active if self.require_active else False

    @property
    def unauthenticated(self):
        """What response to return upon failing authentication."""
        return HttpResponse(status=constants.FORBIDDEN)


class Basic(Authentication):
    """Implementation of the Authentication protocol for BASIC authentication.
    """

    def __init__(self,
                username='username',
                password='password',
                realm='flapjack:api',
                **kwargs
            ):
        #! WWW realm to declare upon returning a 401.
        self.realm = realm

        #! Username field to use to authn with.
        self.username = username

        #! Password field to use to authn with.
        self.password = password

        # Super us up
        super(Basic, self).__init__(self, **kwargs)

    @property
    def unauthenticated(self):
        """What response to return upon failing authentication."""
        response = HttpResponse(status=constants.UNAUTHORIZED)
        response['WWW-Authenticate'] = 'Basic Realm="{}"'.format(self.realm)
        return response

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None."""
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            # No headers; no dice
            return None

        try:
            method, credentials = header.split(' ', 1)
            if not method.lower() == 'basic':
                # Don't handle it -- go away
                return None

            credentials = credentials.strip().decode('base64')
            username, password = credentials.split(':', 1)
        except:
            # Something weird was shoved in the header; no dice
            return None

        # Try and authenticate; we get a user -- shiny
        user = authenticate(**{
                self.username: username,
                self.password: password,
            })

        if user is None:
            # No user; no dice.
            return None

        if not self.is_active(user):
            # User isn't active (and we care); no dice.
            return None

        # Return the user object.
        return user
