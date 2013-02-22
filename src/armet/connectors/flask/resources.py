# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet import utils
from armet.resources import base


class ResourceBase(base.ResourceBase):
    pass


class Resource(six.with_metaclass(ResourceBase, base.Resource)):
    """Specializes the RESTFul resource protocol for flask.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    @classmethod
    def view(cls, *args, **kwargs):
        return "Hello, FLASK!"

    @classmethod
    def mount(cls, app, url, name=None):
        """
        Mounts the resource in the Flask container at the specified
        mount point.
        """
        # Generate a name to use to mount this resource.
        if name is None:
            name = '{}.{}'.format(cls.__module__, cls.__name__)
            name = '{}:{}:{}'.format('armet', name, cls.name)

        # Mount this resource
        rule = '{}{}'.format(url, cls.name)
        app.add_url_rule(rule=rule, endpoint=name, view_func=cls.view)
        app.add_url_rule(rule='{}/<path:path>'.format(rule),
            endpoint='{}:path'.format(name), view_func=cls.view)
