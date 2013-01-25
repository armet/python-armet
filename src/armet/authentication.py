# -*- coding: utf-8 -*-
"""
Describes the authentication protocols and generalizations used to
authenticate access to a resource endpoint.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import hashlib
import abc
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
import six
from . import http, utils, exceptions

import os
import time
import urlparse


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

        except (AttributeError, ValueError):
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
            'authentication.http.realm', 'django:armet')

    @property
    def Unauthenticated(self):
        if self.challenge:
            # Issue the proper challenge response that informs the client
            # that they need to authenticate (allowing a browser to respond
            # with a login prompt for example).
            return exceptions.Unauthorized(self.realm)

        else:
            # Requested to not issue the challenge; concede and let
            # our super report the status.
            return super(Http, self).Unauthenticated


class Basic(Http):
    """Implementation of the Authentication protocol for BASIC authentication.
    """

    def __init__(self, **kwargs):
        """Initialize this and store any needed properties."""
        super(Basic, self).__init__(**kwargs)

        #! Username attribute to use to authn with.
        self.username = utils.config_fallback(kwargs.get('username'),
            'authentication.basic.username', 'username')

        #! Password attribute to use to authn with.
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


class Digest(Http):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.last_nonce = ''
        self.nonce_count = 0
        self.chal = {}

    def build_digest_header(self, method, url):

        realm = self.chal['realm']
        nonce = self.chal['nonce']
        qop = self.chal.get('qop')
        algorithm = self.chal.get('algorithm', 'MD5')
        opaque = self.chal.get('opaque', None)

        algorithm = algorithm.upper()
        # lambdas assume digest modules are imported at the top level
        if algorithm == 'MD5':
            def md5_utf8(x):
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.md5(x).hexdigest()
            hash_utf8 = md5_utf8
        elif algorithm == 'SHA':
            def sha_utf8(x):
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.sha1(x).hexdigest()
            hash_utf8 = sha_utf8
        # XXX MD5-sess
        KD = lambda s, d: hash_utf8("%s:%s" % (s, d))

        if hash_utf8 is None:
            return None

        # XXX not implemented yet
        entdig = None
        p_parsed = urlparse(url)
        path = p_parsed.path
        if p_parsed.query:
            path += '?' + p_parsed.query

        A1 = '%s:%s:%s' % (self.username, realm, self.password)
        A2 = '%s:%s' % (method, path)

        if qop == 'auth':
            if nonce == self.last_nonce:
                self.nonce_count += 1
            else:
                self.nonce_count = 1

            ncvalue = '%08x' % self.nonce_count
            s = str(self.nonce_count).encode('utf-8')
            s += nonce.encode('utf-8')
            s += time.ctime().encode('utf-8')
            s += os.urandom(8)

            cnonce = (hashlib.sha1(s).hexdigest()[:16])
            noncebit = "%s:%s:%s:%s:%s" % (
                nonce, ncvalue, cnonce, qop, hash_utf8(A2))
            respdig = KD(hash_utf8(A1), noncebit)
        elif qop is None:
            respdig = KD(hash_utf8(A1), "%s:%s" % (nonce, hash_utf8(A2)))
        else:
            # XXX handle auth-int.
            return None

        self.last_nonce = nonce

        # XXX should the partial digests be encoded too?
        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
           'response="%s"' % (self.username, realm, nonce, path, respdig)
        if opaque:
            base += ', opaque="%s"' % opaque
        if entdig:
            base += ', digest="%s"' % entdig
            base += ', algorithm="%s"' % algorithm
        if qop:
            base += ', qop=auth, nc=%s, cnonce="%s"' % (ncvalue, cnonce)

        return 'Digest %s' % (base)

    def handle_401(self, r):
        """Takes the given response and tries digest-auth, if needed."""

        num_401_calls = r.request.hooks['response'].count(self.handle_401)
        s_auth = r.headers.get('www-authenticate', '')

        if 'digest' in s_auth.lower() and num_401_calls < 2:

            self.chal = self.parse_dict_header(s_auth.replace('Digest ', ''))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.raw.release_conn()

            r.request.headers['Authorization'] = self.build_digest_header(
                r.request.method, r.request.url)
            _r = r.connection.send(r.request)
            _r.history.append(r)

            return _r

        return r

    def __call__(self, r):
        # If we have a saved nonce, skip the 401
        if self.last_nonce:
            r.headers['Authorization'] = self.build_digest_header(
                r.method, r.url)
        r.register_hook('response', self.handle_401)
        return r

    def parse_dict_header(self, value):
        """Parse lists of key, value pairs as described by RFC
        2068 Section 2 and
        convert them into a python dict:

        >>> d = parse_dict_header('foo="is a fish", bar="as well"')
        >>> type(d) is dict
        True
        >>> sorted(d.items())
        [('bar', 'as well'), ('foo', 'is a fish')]

        If there is no value for a key it will be `None`:

        >>> parse_dict_header('key_without_value')
        {'key_without_value': None}

        To create a header from the :class:`dict` again, use the
        :func:`dump_header` function.

        :param value: a string with a dict header.
        :return: :class:`dict`
        """
        result = {}
        for item in self.parse_list_header(value):
            if '=' not in item:
                result[item] = None
                continue
            name, value = item.split('=', 1)
            if value[:1] == value[-1:] == '"':
                value = self.unquote_header_value(value[1:-1])
            result[name] = value
        return result

    # From mitsuhiko/werkzeug (used with permission).
    def unquote_header_value(self, value, is_filename=False):
        r"""Unquotes a header value.  (Reversal of :func:`quote_header_value`).
        This does not use the real unquoting but what browsers are actually
        using for quoting.

        :param value: the header value to unquote.
        """
        if value and value[0] == value[-1] == '"':
            # this is not the real unquoting, but fixing this so that the
            # RFC is met will result in bugs with internet explorer and
            # probably some other browsers as well.  IE for example is
            # uploading files with "C:\foo\bar.txt" as filename
            value = value[1:-1]

            # if this is a filename and the starting characters look like
            # a UNC path, then just return the value without quotes.  Using the
            # replace sequence below on a UNC path has the effect of turning
            # the leading double slash into a single slash and then
            # _fix_ie_filename() doesn't work correctly.  See #458.
            if not is_filename or value[:2] != '\\\\':
                return value.replace('\\\\', '\\').replace('\\"', '"')
