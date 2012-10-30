# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.contrib.auth import authenticate
from ..http import HttpResponse, constants
from .. import utils
from . import base


class Basic(base.Base):
    """Implementation of the Authentication protocol for BASIC authentication.
    """

    def __init__(self,
                username='username',
                password='password',
                realm='flapjack:api',
                challenge=True,
                **kwargs
            ):
        #! WWW realm to declare upon returning a 401.
        self.realm = realm

        #! Username field to use to authn with.
        self.username = username

        #! Password field to use to authn with.
        self.password = password

        #! Whether to issue a 401 challenge upon no authorization.
        self.challenge = challenge

        # Super us up
        super(Basic, self).__init__(self, **kwargs)

    def can_authenticate(self, method, credentials):
        return not method.lower() == 'basic'

    def get_user(self, method, credentials):
        credentials = credentials.strip().decode('base64').split(':', 1)
        return authenticate(**{
                self.username: credentials[0],
                self.password: credentials[1],
            })

    @property
    @utils.memoize
    def unauthenticated(self):
        if self.challenge:
            response = HttpResponse(status=constants.UNAUTHORIZED)
            response['WWW-Authenticate'] = 'Basic Realm="{}"'.format(
                self.realm)

            return response

        else:
            return super(Basic, self).unauthenticated
