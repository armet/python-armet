# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.exceptions import ImproperlyConfigured
from armet.http import exceptions


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.Session = meta.get('Session')
        if not self.Session:
            raise ImproperlyConfigured(
                'A session factory (via sessionmaker) is required by '
                'the SQLAlchemy model connector.')


class ModelResource(object):
    """Specializes the RESTFul model resource protocol for SQLAlchemy.

    @note
        This is not what you derive from to create resources. Import
        ModelResource from `armet.resources` and derive from that.
    """

    def __init__(self, *args, **kwargs):
        # Let the base resource prepare us.
        super(ModelResource, self).__init__(*args, **kwargs)

        # Instantiate a session using our session object.
        self.session = self.meta.Session()

    def read(self):
        # Initialize the queryset to the model manager.
        queryset = self.session.query(self.meta.model)

        if self.slug is not None:
            name = self.meta.slug.path
            if '.' in name:
                # TODO: Implement relations.
                raise NotImplemented

            # Attempt to filter out and retrieve the specific
            # item referenced by the slug.
            obj = queryset.filter_by(**{name: self.slug}).first()

            if obj:
                # Found something; return it.
                return obj

            # We found nothing; return Not Found - 404.
            raise exceptions.NotFound()

        # Return the entire queryset.
        return queryset.all()
