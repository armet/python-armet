# -*- coding: utf-8 -*-
"""
Describes the authentication protocols and generalizations used to
authenticate access to a resource endpoint.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import hashlib
import abc
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User
import six
import hmac
import uuid
import python_digest
import os
import time
import urlparse
from . import http, utils, exceptions


class Authentication(object):
    """Describes the base authentication protocol.
    """

    def __init__(self, **kwargs):
        """
        Initializes any configuration properties specific for this
        authentication protocol.
        """
        #! Whether to require users to have `is_active` flags in django set to
        #! `True`.
        self.require_active = kwargs.get('require_active', True)

        #! Whether to allow anonymous users being returned from `authenticate`.
        self.allow_anonymous = kwargs.get('allow_anonymous', True)

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None.

        @retval None           Unable to authenticate.
        @retval AnonymousUser  Able to authenticate but failed.
        @retval User           User object representing the curretn user.
        """
        return AnonymousUser()

    def is_active(self, user):
        """Checks if the user is active; served as a point of extension."""
        return user.is_active if self.require_active else False

    @property
    def Unauthenticated(self):
        """The response to return upon failing authentication."""
        return exceptions.NetworkAuthenticationRequired()


class Header(six.with_metaclass(abc.ABCMeta, Authentication)):
    """
    Describes an abstract authentication protocol that uses the `Authorization`
    HTTP/1.1 header.
    """

    def __init__(self, **kwargs):
        if 'allow_anonymous' not in kwargs:
            # Unless explictly allowed; anon accesses are disallowed.
            kwargs['allow_anonymous'] = False

        super(Header, self).__init__(**kwargs)

    def authenticate(self, request):
        """Gets the a user if they are authenticated; else None.

        @retval None           Unable to authenticate.
        @retval AnonymousUser  Able to authenticate but failed.
        @retval User           User object representing the current user.
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        try:
            method, credentials = header.split(' ', 1)
            if not self.can_authenticate(method.strip(), request):
                # We are unable to (for whatever reason) make an informed
                # authentication descision using these as criterion
                return None

            user = self.get_user(credentials.strip(), request)
            if user is None or not self.is_active(user):
                # No user was retrieved or the retrieved user was deemed
                # to be inactive.
                return AnonymousUser()

            return user

        except (AttributeError, ValueError):
            # Something went wrong and we were unable to authenticate;
            # possible reasons include:
            #   - No `authorization` header present
            return None

    @abc.abstractmethod
    def can_authenticate(self, method, request):
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
    def get_user(self, credentials, request):
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
            'authentication.http.realm', 'django:armet')

        #! Username attribute to use to authn with.
        self.username = utils.config_fallback(kwargs.get('username'),
            'authentication.basic.username', 'username')


class Basic(Http):
    """Implementation of the Authentication protocol for BASIC authentication.
    """

    def can_authenticate(self, method, *args):
        return method.lower() == 'basic'

    def get_user(self, credentials, *args):
        username, password = credentials.decode('base64').split(':', 1)
        return authenticate(**{
            self.username: username,
            'password': password,
        })

    @property
    def Unauthenticated(self):
        if self.challenge:
            # Issue the proper challenge response.
            raise exceptions.Unauthorized('Basic Realm="{}"'.format(
                self.realm))

        else:
            # Requested to not issue the challenge; give it up the chain.
            return super(Basic, self).Unauthenticated


class Digest(Http):
    """Implementation of the Authentication protocol for DIGEST authentication.

    FIXME: DIGEST Authentication requires a partial digest hash to be stored
    that is the hash of the username, realm, and password. We need to figure
    something out that will allow it to be stored per user per realm and
    only stored if digest authentication is used.

    @par Reference
     - https://bitbucket.org/akoha/django-digest/src/tip/django_digest/
    """

    def get_user(self, credentials, request, *args):
        # Parse the credentials in the digest header.
        digest = python_digest.parse_digest_response(credentials)

        # Validate the realm.
        if digest.realm != self.realm:
            return None

        # Validate the nonce.
        if not python_digest.validate_nonce(digest.nonce, settings.SECRET_KEY):
            return None

        try:
            # Attempt to find the matched user
            user = User.objects.get(**{self.username: digest.username})

        except User.DoesNotExist:
            return None

        # TODO: Retrieve the partial digest for this user.
        partial = None

        # Construct and validate the partial digest.
        expected = python_digest.calculate_request_digest(
            method=request.method, digest_response=digest,
            partial_digest=partial)
        if expected != digest.response:
            return None

        # Apparently we are successfully authenticated.
        return user

    def can_authenticate(self, method, *args):
        return method.lower() == 'digest'

    @property
    def Unauthenticated(self):
        if self.challenge:
            # Build the challenge.
            sh1 = hashlib.sha1
            opaque = hmac.new(str(uuid.uuid4()), digestmod=sha1).hexdigest()
            challenge = python_digest.build_digest_challenge(
                time.time(), settings.SECRET_KEY, self.realm, opaque, False)

            # Issue the proper challenge response.
            raise exceptions.Unauthorized(challenge)

        else:
            # Requested to not issue the challenge; give it up the chain.
            return super(Digest, self).Unauthenticated
