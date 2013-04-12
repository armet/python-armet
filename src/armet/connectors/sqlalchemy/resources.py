# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet.exceptions import ImproperlyConfigured
from armet.http import exceptions
# from armet.resources.query import Query


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.engine = meta.get('engine')
        if not self.engine:
            raise ImproperlyConfigured(
                'No engine specified for a model resource using SQLAlchemy.')

        # Instantiate the sessionmaker and bind it to the engine.
        from sqlalchemy.orm import sessionmaker
        self.session = sessionmaker(bind=self.engine)


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
        self.session = self.meta.session()

    # def filter(self, iterable, query):
    #     return iterable

    def read(self):
        # Initialize the queryset to the model manager.
        # queryset = self.meta.model.objects
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

        # else:
        #     # The slug is not none; the resource is being accessed
        #     # as a resource (eg. GET /poll).

        #     if self.request.query:
        #         # The request has a query (eg. GET /poll?...).
        #         # Send it off to the query string parser and then
        #         # off to the filterer to construct the appropriate expression
        #         # and filter our queryable.
        #         queryset = self.filter(queryset, Query(self.requset.query))

        # Return the entire queryset.
        return queryset.all()
