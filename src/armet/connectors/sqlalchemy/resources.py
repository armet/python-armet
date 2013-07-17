# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import operator
from armet.exceptions import ImproperlyConfigured
from armet.query import parser, Query, QuerySegment, constants


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

    # def __init__(self, *args, **kwargs):
    #     # Let the base resource prepare us.
    #     super(ModelResource, self).__init__(*args, **kwargs)

    def __init__(self):
        # Instantiate a session using our session object.
        self.session = self.meta.Session()

    @classmethod
    def _filter_segment(cls, model, path, operation, values, attr):
        expression = None
        segment = path.pop(0)

        # Get the associated column.
        col = model.__dict__[segment]

        # Do we have any path segments left?
        if path:
            # We need to evaluate these inner-outer.
            expression = cls._filter_segment(
                col.property.mapper.class_, path,
                operation, values,
                attr)

            # Apply the expression.
            return col.has(expression)

        # Determine the operation.
        if operation == constants.OPERATOR_EQUAL[0]:
            op = operator.eq

        elif operation == constants.OPERATOR_IEQUAL[0]:
            if issubclass(attr.type, bool):
                # Doesn't make sense for :iequal to work anyway
                # on booleans.
                op = operator.eq

            else:
                op = lambda x, y: x.ilike(y)

        elif operation == constants.OPERATOR_ISNULL[0]:
            op = lambda x, y: (x.is_(None)) if y else (~x.is_(None))

        elif operation == constants.OPERATOR_LT[0]:
            op = operator.lt

        elif operation == constants.OPERATOR_GT[0]:
            op = operator.gt

        elif operation == constants.OPERATOR_LTE[0]:
            op = operator.le

        elif operation == constants.OPERATOR_GTE[0]:
            op = operator.ge

        elif operation == constants.OPERATOR_REGEX[0]:
            # TODO: We need to do something.. this only really works in
            #   mysql; wtf does django do?
            op = lambda x, y: x.op('REGEXP')(y)

        for index, value in enumerate(values):
            value = attr.try_clean(value)
            if index:
                # Not the first one; OR it against the
                # existing expression.
                expression |= op(col, value)
            expression = op(col, value)

        # Return the constructed expression.
        return expression

    @classmethod
    def _filter(cls, segments, clause=None, last=None, attribute=None):
        # Set some process variables.
        clause = clause
        last = last

        # Iterate through each query segment.
        for segment in segments:
            if isinstance(segment, collections.Iterable):
                # This is a nested query.
                expression = cls._filter(segment)

            else:
                # Munge the initial path segment through the
                # attribute dictionary.
                attr = attribute
                if attr is None:
                    attr = cls.attributes[segment.path[0]]
                    del segment.path[0]
                    segment.path[0:0] = attr.path.split('.')

                # Construct an expression.
                expression = cls._filter_segment(
                    cls.meta.model, segment.path,
                    segment.operator, segment.values, attr)

            if last:
                # Combine the clause with the current expression using the
                # last combinator.
                clause = last.combinator(clause, expression)
                last = segment

            else:
                # The first clause; set it.
                clause = expression
                last = segment

        # Return the constructed clause.
        return clause

    def read(self):
        # Initialize the query to the model manager.
        obj = self.session.query(self.meta.model)

        # Check if we need to filter the query object in some way.
        query = None
        if self.slug is not None:
            # Manually construct a query that would represent a query by
            # the slug.
            query = Query(segments=[QuerySegment(
                path=self.meta.slug.path.split('.'),
                operator=constants.OPERATOR_EQUAL[0],
                values=[self.slug])])

            # Apply and return the resultant item.
            clause = self._filter(query.segments, attribute=self.meta.slug)
            return obj.filter(clause).first()

        elif self.request.query:
            # The request has a query (eg. GET /poll?...).
            # Send it off to the query string parser and then
            # off to the filterer to construct the appropriate expression
            # and filter our queryable.
            query = parser.parse(self.request.query)

            # Apply and return the resultant items.
            clause = self._filter(query.segments)
            return obj.filter(clause).distinct().all()

        # Evaluate and return all items.
        return obj.all()
