# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.contrib.auth import authenticate
from ..http import HttpResponse, constants
from .. import utils
from . import header


class Basic(header.Header):
    """Implementation of the Authentication protocol for BASIC authentication.

    @par Reference
     - RFC 2617 [http://www.ietf.org/rfc/rfc2617.txt]
    """

    def __init__(self, **kwargs):
        """Initialize this and store any needed properties."""
        super(Basic, self).__init__(**kwargs)

        #! Whether to issue a 401 challenge upon no authorization.
        self.challenge = utils.config_fallback(kwargs.get('challenge'),
            'authentication.basic.challenge', True)

        #! WWW realm to declare upon challenge.
        self.realm = utils.config_fallback(kwargs.get('realm'),
            'authentication.basic.realm', 'django:flapjack')

        #! Username field to use to authn with.
        self.username = utils.config_fallback(kwargs.get('username'),
            'authentication.basic.username', 'django:flapjack')

        #! Password field to use to authn with.
        self.password = utils.config_fallback(kwargs.get('password'),
            'authentication.basic.password', 'django:flapjack')

    def can_authenticate(self, method, credentials):
        return method.lower() == 'basic'

    def get_user(self, method, credentials):
        username, password = credentials.strip().decode('base64').split(':', 1)
        return authenticate(**{
                self.username: username,
                self.password: password,
            })

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
            return super(Basic, self).unauthenticated
