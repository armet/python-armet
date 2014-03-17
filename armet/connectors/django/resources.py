# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
import six
from six.moves import map, reduce
from django.conf import urls
from django.db.models import Q
from django.views.decorators import csrf
from armet import utils
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
            gevent.spawn(super(Resource, cls).view, request, response)

            # Construct and return the generator response.
            response._handle.content = cls.stream(response, response)
            return response._handle

        # Pass control off to the resource handler.
        result = super(Resource, cls).view(request, response)

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
    constants.OPERATOR_EQUAL: '__exact',
    constants.OPERATOR_IEQUAL: '__iexact',
    constants.OPERATOR_LT: '__lt',
    constants.OPERATOR_GT: '__gt',
    constants.OPERATOR_LTE: '__lte',
    constants.OPERATOR_GTE: '__gte',
}

# import ipdb; ipdb.set_trace()
# Rewire the map.
OPERATOR_MAP = dict(
    (constants.OPERATOR_MAP[k], v) for k, v in OPERATOR_MAP.items()
)


def segment_query(seg, attributes):

    # Get the attribute in question.
    attribute = attributes[seg.path[0]]

    # Replace the initial path segment with the expanded
    # attribute path.
    seg.path[0:1] = attribute.path.split('.')

    # Boolean's should use `exact` rather than `iexact`.
    if attribute.type is bool:
        op = '__exact'
    else:
        op = OPERATOR_MAP[seg.operator]

    # Build the path from the segment.
    path = '__'.join(seg.path) + op

    # Construct a Q-object from the segment.
    return reduce(operator.or_,
                  map(lambda x: Q((path, x)),
                      map(attribute.try_clean, seg.values)))


def noop_query(*args):
    return Q()


def unary_query(query, *args):
    return query.operation(build_clause(query.operand, *args))


def binary_query(query, *args):
    return query.operation(
        build_clause(query.left, *args),
        build_clause(query.right, *args))


CLAUSE_MAP = {
    parser.NoopQuerySegment: noop_query,
    parser.BinarySegmentCombinator: binary_query,
    parser.UnarySegmentCombinator: unary_query,
    parser.QuerySegment: segment_query,
}


def build_clause(query, attributes):
    class_ = type(query) if not isinstance(query, type) else query
    fn = CLAUSE_MAP.get(class_)
    if fn is not None:
        return fn(query, attributes)
    elif issubclass(class_, Query):
        return build_clause(query.parsed, attributes)
    else:
        raise ValueError('Unable to translate query node %s' % str(query))

# def build_clause(query, attributes):
#     # Iterate through each query segment.
#     clause = None
#     last = None
#     for seg in query.segments:
#         # Get the attribute in question.
#         attribute = attributes[seg.path[0]]

#         # Replace the initial path segment with the expanded
#         # attribute path.
#         seg.path[0:1] = attribute.path.split('.')

#         # Boolean's should use `exact` rather than `iexact`.
#         if attribute.type is bool:
#             op = '__exact'
#         else:
#             op = OPERATOR_MAP[seg.operator]

#         # Build the path from the segment.
#         path = '__'.join(seg.path) + op

#         # Construct a Q-object from the segment.
#         q = reduce(operator.or_,
#                    map(lambda x: Q((path, x)),
#                        map(attribute.try_clean, seg.values)))

#         # Combine the segment with the last.
#         clause = last.combinator(clause, q) if last is not None else q
#         last = seg

#     # Return the constructed clause.
#     return clause


class ModelResource(object):

    def filter(self, clause, queryset):
        # Filter the queryset by the passed clause.
        return queryset.filter(clause).distinct()

    def count(self, queryset):
        # Return the count of the queryset.
        return len(queryset)

    def read(self):
        # Initialize the queryset to the model manager.
        queryset = self.meta.model.objects

        query = None
        if self.slug is not None:
            # This is an item-access (eg. GET /<name>/:slug); ignore the
            # query string and generate a query-object based on the slug.
            query = Query(
                original=None,
                parsed=QuerySegment(
                    path=self.meta.slug.path.split('.'),
                    operator=constants.OPERATOR_MAP[constants.OPERATOR_EQUAL],
                    values=[self.slug]
                )
            )

        elif self.request.query:
            # This is a list-access; use the query string and construct
            # a query object from it.
            query = parser.parse(self.request.query)

        # Determine if we need to filter the queryset in some way; and if so,
        # filter it.
        if query is not None:
            clause = build_clause(query, self.attributes)
            queryset = self.filter(clause, queryset)

        # Filter the queryset by asserting authorization.
        queryset = self.meta.authorization.filter(
            self.request.user, 'read', self, queryset)

        if self.slug is not None:
            # Attempt to return just the single result we should have.
            result = queryset.all()[:1]
            return result[0] if result else None

        # Return the entire queryset.
        return queryset.all()

    def create(self, data):
        # Instantiate a new target.
        target = self.meta.model()

        # Iterate through all attributes and set each one.
        for name, attribute in six.iteritems(self.attributes):
            # Set each one on the target.
            value = data.get(name)
            if value is not None:
                attribute.set(target, value)

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'create', self, target):
            authz.unauthorized()

        # Save the target.
        target.save()

        # Return the target.
        return target

    def update(self, target, data):
        # Iterate through all attributes and set each one.
        for name, attribute in six.iteritems(self.attributes):
            # Set each one on the target.
            attribute.set(target, data.get(name))

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'update', self, target):
            authz.unauthorized()

        # Save the target.
        target.save()

    def destroy(self):
        # Grab the existing target.
        target = self.read()

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'destroy', self, target):
            authz.unauthorized()

        # Destroy the target.
        target.delete()
