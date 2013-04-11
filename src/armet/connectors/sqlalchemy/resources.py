# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet.exceptions import ImproperlyConfigured


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.session = meta.get('session')
        if not self.session:
            raise ImproperlyConfigured(
                'No session specified for a model resource using SQLAlchemy.')


class ModelResource(object):
    """Specializes the RESTFul model resource protocol for SQLAlchemy.

    @note
        This is not what you derive from to create resources. Import
        ModelResource from `armet.resources` and derive from that.
    """

    def read(self):
        # Initialize the queryset to the model manager.
        # queryset = self.meta.model.objects
        queryset = self.meta.session(self.meta.model)

        # if self.slug is not None:
        #     name = self.meta.slug.path.replace('.', '__')
        #     try:
        #         # Attempt to filter out and retrieve the specific
        #         # item referenced by the slug.
        #         return queryset.get(**{name: self.slug})

        #     except:
        #         # We found nothing; return Not Found - 404.
        #         raise exceptions.NotFound()

        # Return the entire queryset.
        return queryset.all()
