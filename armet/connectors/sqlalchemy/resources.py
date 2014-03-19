# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import operator
from functools import partial
from copy import deepcopy
from six.moves import map, reduce
from armet.exceptions import ImproperlyConfigured
from armet.query import parser, Query, QuerySegment, constants
from sqlalchemy.exc import InvalidRequestError
import sqlalchemy as sa


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.Session = meta.get('Session')
        if not self.Session:
            raise ImproperlyConfigured(
                'A session factory (via sessionmaker) is required by '
                'the SQLAlchemy model connector.')


def iequal_helper(x, y):
    # String values should use ILIKE queries.
    if isinstance(type(y), six.string_types):
        return x.ilike(y)
    else:
        return operator.eq(x, y)


# Build an operator map to use for sqlalchemy.
OPERATOR_MAP = {
    constants.OPERATOR_EQUAL: operator.eq,
    constants.OPERATOR_IEQUAL: iequal_helper,
    constants.OPERATOR_LT: operator.lt,
    constants.OPERATOR_GT: operator.gt,
    constants.OPERATOR_LTE: operator.le,
    constants.OPERATOR_GTE: operator.ge,
}

# Rewire the map.
OPERATOR_MAP = dict(
    (constants.OPERATOR_MAP[k], v) for k, v in OPERATOR_MAP.items()
)


def build_segment(model, segment, attr, clean):
    # Get the associated column for the initial path.
    path = segment.path.pop(0)
    col = getattr(model, path)

    # Resolve the inner-most path segment.
    if segment.path:
        if col.impl.accepts_scalar_loader:
            return col.has(build_segment(
                col.property.mapper.class_, segment, attr, clean))

        else:
            try:
                return col.any(build_segment(
                    col.property.mapper.class_, deepcopy(segment),
                    attr, clean))

            except InvalidRequestError:
                return col.has(build_segment(
                    col.property.mapper.class_, deepcopy(segment),
                    attr, clean))

    # Determine the operator.
    op = OPERATOR_MAP[segment.operator]

    # Apply the operator to the values and return the expression
    qs = reduce(operator.or_,
                map(partial(op, col),
                    map(lambda x: clean(attr.try_clean(x)), segment.values)))

    # Apply the negation.
    if segment.negated:
        qs = ~qs

    # Return our query object.
    return qs


def segment_query(resource, segment, attributes, cleaners, model):

    attribute = attributes[segment.path[0]]

    # Modify the segment's to reflect what the attribute was declared for.
    segment.path[0:1] = attribute.path.split('.')

    # Create a cleaner that can work here.
    clean = partial(cleaners[attribute.name], resource)

    # Dispatch to the recursive segment building function
    return build_segment(model, segment, attribute, clean)


def noop_query(*args):
    return sa.sql.true()


def unary_query(resource, query, *args):
    return query.operation(build_clause(resource, query.operand, *args))


def binary_query(resource, query, *args):
    return query.operation(
        build_clause(resource, query.left, *args),
        build_clause(resource, query.right, *args))


CLAUSE_MAP = {
    parser.NoopQuerySegment: noop_query,
    parser.BinarySegmentCombinator: binary_query,
    parser.UnarySegmentCombinator: unary_query,
    parser.QuerySegment: segment_query,
}


def build_clause(resource, query, attributes, cleaners, model):
    class_ = type(query) if not isinstance(query, type) else query
    fn = CLAUSE_MAP.get(class_)
    if fn is not None:
        return fn(resource, query, attributes, cleaners, model)
    elif issubclass(class_, Query):
        return build_clause(
            resource,
            query.parsed,
            attributes,
            cleaners,
            model)
    else:
        raise ValueError('Unable to translate query node %s' % str(query))


class ModelResource(object):
    """Specializes the RESTFul model resource protocol for SQLAlchemy.

    @note
        This is not what you derive from to create resources. Import
        ModelResource from `armet.resources` and derive from that.
    """

    def route(self, *args, **kwargs):
        # Establish a session.
        self.session = session = self.meta.Session()

        try:
            # Continue on with the cycle.
            result = super(ModelResource, self).route(*args, **kwargs)

            # Commit the session.
            session.commit()

            # Return the result.
            return result

        except:
            # Something occurred; rollback the session.
            session.rollback()

            # Re-raise the exception.
            raise

        finally:
            # Close the session.
            session.close()

    def filter(self, clause, queryset):
        # Filter the queryset by the passed clause.
        return queryset.filter(clause).distinct()

    def count(self, queryset):
        # Return the count of the queryset.
        return queryset.count()

    def read(self):
        # Initialize the query to the model.
        queryset = self.session.query(self.meta.model)

        query = None
        if self.slug is not None:
            # This is an item-access (eg. GET //:slug); ignore the
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
        clause = None
        if query is not None:
            clause = build_clause(
                self, query, self.attributes,
                self.cleaners, self.meta.model)

            queryset = self.filter(clause, queryset)

        if self.slug is None:
            # Filter the queryset by asserting authorization.
            queryset = self.meta.authorization.filter(
                self.request.user, 'read', self, queryset)

            # Return the queryset.
            return queryset

        else:
            # Get the item in question.
            item = queryset.first()

            # Ensure the user is authorized to perform this action.
            authz = self.meta.authorization
            if not authz.is_authorized(self.request.user, 'read', self, item):
                authz.unauthorized()

            # We're good, return the item.
            return item

    def create(self, data):
        # Instantiate a new target.
        target = self.meta.model()

        # Iterate through all attributes and set each one.
        for name, attribute in six.iteritems(self.attributes):
            # Set each one on the target.
            value = data.get(name)
            if value is not None:
                attribute.set(target, value)

        # Add the target to the session.
        self.session.add(target)
        self.session.flush()

        # Refresh the target object to avoid inconsistencies with storage.
        self.session.expire(target)

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'create', self, target):
            authz.unauthorized()

        # Return the target.
        return target

    def update(self, target, data):
        # Iterate through all attributes and set each one.
        for name, attribute in six.iteritems(self.attributes):
            # Set each one on the target.
            attribute.set(target, data.get(name))

        # Flush the target and expire attributes.
        self.session.flush()

        # Refresh the target object to avoid inconsistencies with storage.
        self.session.expire(target)

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'update', self, target):
            authz.unauthorized()

    def destroy(self):
        # Grab the existing target.
        target = self.read()

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'destroy', self, target):
            authz.unauthorized()

        # Remove the object from the session.
        self.session.delete(target)
