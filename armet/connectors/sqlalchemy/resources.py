# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import operator
from functools import partial
from six.moves import map, reduce
from armet.exceptions import ImproperlyConfigured
from armet.query import parser, Query, QuerySegment, constants
from armet import utils


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
    constants.OPERATOR_EQUAL[0]: operator.eq,
    constants.OPERATOR_IEQUAL[0]: iequal_helper,
    constants.OPERATOR_LT[0]: operator.lt,
    constants.OPERATOR_GT[0]: operator.gt,
    constants.OPERATOR_LTE[0]: operator.le,
    constants.OPERATOR_GTE[0]: operator.ge,
}


def build_segment(model, segment, attr):
    # Get the associated column for the initial path.
    path = segment.path.pop(0)
    col = model.__dict__[path]

    # Resolve the inner-most path segment.
    if segment.path:
        return col.has(build_segment(
            col.property.mapper.class_, segment, attr))

    # Determine the operator.
    op = OPERATOR_MAP[segment.operator]

    # Apply the operator to the values and return the expression
    return reduce(operator.or_,
                  map(partial(op, col),
                      map(attr.try_clean, segment.values)))


def build_clause(query, attributes, model):
    # Iterate through each query segment.
    clause = None
    last = None
    for seg in query.segments:
        # Get the attribute in question.
        attribute = attributes[seg.path[0]]

        # Replace the initial path segment with the expanded
        # attribute path.
        seg.path[0:1] = attribute.path.split('.')

        # Construct the clause from the segment.
        q = build_segment(model, seg, attribute)

        # Combine the segment with the last.
        clause = last.combinator(clause, q) if last is not None else q
        last = seg

    # Return the constructed clause.
    return clause


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
            result = utils.super(ModelResource, self).route(*args, **kwargs)

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

    def read(self):
        # Initialize the query to the model.
        queryset = self.session.query(self.meta.model)

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
        clause = None
        if query is not None:
            clause = build_clause(query, self.attributes, self.meta.model)
            queryset = self.filter(clause, queryset)

        # Filter the queryset by asserting authorization.
        queryset = self.meta.authorization.filter(
            self.request.user, 'read', self, queryset)

        # Return the queryset.
        return queryset.all() if self.slug is None else queryset.first()

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

        # Add the target to the session.
        self.session.add(target)
        self.session.flush()

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

        # Flush the target and expire attributes.
        self.session.flush()
        
        # Refresh the target object to avoid inconsistencies with storage.
        self.session.expire(target)

    def destroy(self):
        # Grab the existing target.
        target = self.read()

        # Ensure the user is authorized to perform this action.
        authz = self.meta.authorization
        if not authz.is_authorized(self.request.user, 'destroy', self, target):
            authz.unauthorized()

        # Remove the object from the session.
        self.session.delete(target)
