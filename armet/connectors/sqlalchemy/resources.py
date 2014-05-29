# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import operator
from functools import partial
from collections import Iterable
from copy import deepcopy
from six.moves import map, reduce
from armet.exceptions import ImproperlyConfigured
from armet.query import parser, Query, QuerySegment, constants
from armet.http.exceptions import BadRequest
from sqlalchemy.exc import InvalidRequestError
import sqlalchemy as sa
import functools


class ModelResourceOptions(object):

    def __init__(self, meta, name, bases):
        #! SQLAlchemy session used to perform operations on the models.
        self.Session = meta.get('Session')
        if not self.Session:
            raise ImproperlyConfigured(
                'A session factory (via sessionmaker) is required by '
                'the SQLAlchemy model connector.')


def ilike_helper(default):
    """Helper function that performs an `ilike` query if a string value
    is passed, otherwise the normal default operation."""
    @functools.wraps(default)
    def wrapped(x, y):
        # String values should use ILIKE queries.
        if isinstance(y, six.string_types) and not isinstance(x.type, sa.Enum):
            return x.ilike("%" + y + "%")
        else:
            return default(x, y)
    return wrapped


# Build an operator map to use for sqlalchemy.
OPERATOR_MAP = {
    constants.OPERATOR_EQUAL: operator.eq,
    constants.OPERATOR_IEQUAL: ilike_helper(operator.eq),
    constants.OPERATOR_LT: operator.lt,
    constants.OPERATOR_GT: operator.gt,
    constants.OPERATOR_LTE: operator.le,
    constants.OPERATOR_GTE: operator.ge,
    constants.OPERATOR_ICONTAINS: ilike_helper(operator.contains),
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

            # Sanity check to make sure some item was found.
            if item is None:
                return None

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

        # Iterate through all write-able relations and set each one.
        for name, relation in six.iteritems(self.relationships):
            if relation.write:
                # Set each one on the target.
                value = data.get(name)
                if value is not None:
                    # FIXME: Use some deferred thing that is not `setattr`.
                    setattr(target, relation.key, value)

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

        # Iterate through all write-able relations and set each one.
        for name, relation in six.iteritems(self.relationships):
            if relation.write:
                # Set each one on the target.
                # FIXME: Use some deferred thing that is not `setattr`.
                setattr(target, relation.key, data.get(name))

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

    def _resolve_relation(self, target):
        # Resolve the relationship key.
        key = None
        related = type(self)._related_models
        res_clss = type(target),
        while res_clss:
            res_cls_next = []
            for res_cls in res_clss:
                if res_cls in related:
                    key = self.relationships[related[res_cls]].key
                    break

                if res_cls.__bases__:
                    res_cls_next.extend(res_cls.__bases__)

            else:
                # Nope; continue
                res_clss = res_cls_next
                continue

            # Able to link
            break

        else:
            # Not able to link
            return None

        # Able to link
        return key

    def relate(self, target, other):
        # Resolve the relationship key.
        key = self._resolve_relation(other)
        if not key:
            raise BadRequest({
                '__all__': "Unable to link a '%s' to a '%s'." % (
                    type(target).__name__, type(other).__name__)})

        # Grab the set_ in question.
        set_ = getattr(target, key)

        # Append the relationship.
        set_.append(other)

        # Flush the target and expire attributes.
        self.session.flush()

        # Refresh the target object to avoid inconsistencies with storage.
        self.session.expire(target)

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'update', self, target):
            authz.unauthorized()

    def unrelate(self, target, other):
        # Resolve the relationship key.
        key = self._resolve_relation(other)
        if not key:
            raise BadRequest({
                '__all__': "Unable to link a '%s' to a '%s'." % (
                    type(target).__name__, type(other).__name__)})

        # Grab the set_ in question.
        set_ = getattr(target, key)

        # Append the relationship.
        set_.remove(other)

        # Flush the target and expire attributes.
        self.session.flush()

        # Refresh the target object to avoid inconsistencies with storage.
        self.session.expire(target)

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'update', self, target):
            authz.unauthorized()

    def read_related(self, target, resource, key):
        # Grab the set_ in question.
        set_ = getattr(target, key)

        # Build the related items.
        qs = set_

        if isinstance(qs, Iterable):
            if self.request.user:
                # Filter the queryset by asserting authorization.
                qs = resource.meta.authorization.filter(
                    self.request.user, 'read', resource, qs)

        else:
            if self.request.user:
                # Ensure we can access this.
                authz = self.meta.authorization
                if not authz.is_authorized(
                        self.request.user, 'read', resource, qs):
                    authz.unauthorized()

        # Return the queryset.
        return qs

    def clean_related(self, relation, value):
        # Grab the model in question.
        model = relation.resource.meta.model

        # Attempt to build a query to `get` the model.
        target = self.session.query(model).get(value)
        if target is not None:
            # Found a target from the value.
            return target

        # Found nothing.
