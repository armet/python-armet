# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import map, reduce
from django.conf import urls
from django.db.models import Q
from django.views.decorators import csrf
from armet import utils
from armet.http import exceptions
from . import http
from armet.query import parser, Query, QuerySegment, constants


class Resource(object):

    @classmethod
    @csrf.csrf_exempt
    def view(cls, django_request, *args, **kwargs):
        # Construct request and response wrappers.
        async = cls.meta.asynchronous
        path = kwargs.get('path') or ''
        request = http.Request(django_request, path=path, asynchronous=async)
        response = http.Response(asynchronous=async)

        # Defer the execution thread if we're running asynchronously.
        if async:
            # Defer the view to pass of control.
            import gevent
            gevent.spawn(super(cls.__base__, cls).view, request, response)

            # Construct and return the generator response.
            response._handle.content = cls.stream(response, response)
            return response._handle

        # Pass control off to the resource handler.
        result = super(cls.__base__, cls).view(request, response)

        # Configure the response and return it.
        response._handle.content = result
        return response._handle

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        return urls.patterns('', urls.url(
            r'^{}(?:$|(?P<path>[/:(.].*))'.format(cls.meta.name),
            cls.view,
            name='armet-api-{}'.format(cls.meta.name),
            kwargs={'resource': cls.meta.name}))


# Build an operator map to use for django.
OPERATOR_MAP = {
    constants.OPERATOR_EQUAL[0]: '__exact',
    constants.OPERATOR_IEQUAL[0]: '__iexact',
    constants.OPERATOR_LT[0]: '__lt',
    constants.OPERATOR_GT[0]: '__gt',
    constants.OPERATOR_LTE[0]: '__lte',
    constants.OPERATOR_GTE[0]: '__gte',
}


class ModelResource(object):

    def filter(self, query, queryset):
        # Iterate through each query segment.
        clause = None
        last = None
        for seg in query.segments:
            # Get the attribute in question.
            attribute = self.attributes[seg.path[0]]

            # Replace the initial path segment with the expanded
            # attribute path.
            del seg.path[0]
            seg.path[0:0] = attribute.path.split('.')

            # Build the path from the segment.
            path = '__'.join(seg.path) + OPERATOR_MAP[seg.operator]

            # Construct a Q-object from the segment.
            q = reduce(operator.or_, map(lambda x: Q((path, x)), seg.values))

            # Combine the segment with the last.
            clause = last.combinator(clause, q) if last is not None else q
            last = seg

        # Filter by the constructed clause.
        return queryset.filter(clause).distinct()

    def read(self):
        # Initialize the queryset to the model manager.
        queryset = self.meta.model.objects

        query = None
        if self.slug is not None:
            # This is an item-access (eg. GET /<name>/:slug); ignore the
            # query string and generate a query-object based on the slug.
            query = Query(segments=[QuerySegment(
                path=self.meta.slug.path.split('.'),
                operator=constants.OPERATOR_EQUAL[0],
                values=[self.slug])])

        elif self.request.query:
            # This is a list-access; use the query string and construct
            # a query object from it.
            query = parser.parse(self.request.query)

        # Determine if we need to filter the queryset in some way; and if so,
        # filter it.
        if query is not None:
            queryset = self.filter(query, queryset)

        if self.slug is not None:
            # Attempt to return just the single result we should have.
            result = queryset.all()[:1]
            return result[0] if result else None

        # Return the entire queryset.
        return list(queryset.all())
