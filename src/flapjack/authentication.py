# -*- coding: utf-8 -*-
"""
Describes the authentication protocols and generalizations used to
authenticate access to a resource endpoint.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from .http import HttpResponse, constants
from . import utils


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


class Header(Base):
    """
    Describes an abstract authentication protocol that uses the `Authorization`
    HTTP/1.1 header.
    """

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None.

        @retval None           Unable to authenticate.
        @retval AnonymousUser  Able to authenticate but failed.
        @retval User           User object representing the curretn user.
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        try:
            method, credentials = header.split(' ', 1)
            if not self.can_authenticate(method):
                # We are unable to (for whatever reason) make an informed
                # authentication descision using these as criterion
                return None

            user = self.get_user(credentials)
            if user is None or not self.is_active(user):
                # No user was retrieved or the retrieved user was deemed
                # to be inactive.
                return AnonymousUser()

            return user

        except AttributeError:
            # Something went wrong and we were unable to authenticate;
            # possible reasons include:
            #   - No `authorization` header present
            return None

    @abc.abstractmethod
    def can_authenticate(self, method):
        """Checks if authentication can be asserted with reasonable reliance.

        @retval True
            Indicates that this authentication protocol can assert a user
            with the given credentials with a reasonable confidence.

        @retval False
            Indicates that this authentication protocol cannot assert a user
            and that the authentication process should continue on to the
            next available authentication protocol.
        """
        pass

    @abc.abstractmethod
    def get_user(self, credentials):
        """Retrieves a user using the provided credentials.

        @return
            Returns either the currently authenticated user
            or `AnonymousUser`.
        """
        pass


class Http(Header):
    """
    Generalization of the Authentication protocol for authentication using
    the schemes defined by the HTTP/1.1 standard.

    @par Reference
     - RFC 2617 [http://www.ietf.org/rfc/rfc2617.txt]
    """

    def __init__(self, **kwargs):
        """Initialize this and store any needed properties."""
        super(Http, self).__init__(**kwargs)

        #! Whether to issue a 401 challenge upon no authorization.
        self.challenge = utils.config_fallback(kwargs.get('challenge'),
            'authentication.http.challenge', True)

        #! WWW realm to declare upon challenge.
        self.realm = utils.config_fallback(kwargs.get('realm'),
            'authentication.http.realm', 'django:flapjack')

    @property
    def unauthenticated(self):
        if self.challenge:
            # Issue the proper challenge response that informs the client
            # that they need to authenticate (allowing a browser to respond
            # with a login prompt for example).
            response = HttpResponse(status=constants.UNAUTHORIZED)
            response['WWW-Authenticate'] = \
                'Basic Realm="{}"'.format(self.realm)

            return response

        else:
            # Requested to not issue the challenge; concede and let
            # our super report the status.
            return super(Http, self).unauthenticated


class Basic(Http):
    """Implementation of the Authentication protocol for BASIC authentication.
    """

    def __init__(self, **kwargs):
        """Initialize this and store any needed properties."""
        super(Basic, self).__init__(**kwargs)

        #! Username field to use to authn with.
        self.username = utils.config_fallback(kwargs.get('username'),
            'authentication.basic.username', 'username')

        #! Password field to use to authn with.
        self.password = utils.config_fallback(kwargs.get('password'),
            'authentication.basic.password', 'password')

    def can_authenticate(self, method):
        return method.lower() == 'basic'

    def get_user(self, credentials):
        username, password = credentials.strip().decode('base64').split(':', 1)
        return authenticate(**{
                self.username: username,
                self.password: password,
            })
