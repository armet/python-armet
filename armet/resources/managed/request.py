# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


def read(resource, url):
    """
    Perform a `read` request in the passed `resource` context against
    the given `url`.

    Returns what a `read` would return (the managed target item).
    """
    return resource._request_read(url)
