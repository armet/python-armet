# -*- coding: utf-8 -*-
"""Provide utility methods for easing use of authentication protocols.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
import python_digest


def basic(username, password):
    """
    Generates an appropriate authorization header for use with the BASIC
    authentication protocol.
    """
    credentials = "{}:{}".format(username, password).encode('base64')
    return "Basic {}".format(credentials)
