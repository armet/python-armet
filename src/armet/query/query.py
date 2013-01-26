# -*- coding: utf-8 -*-
"""
Defines the query parser for Armet
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
# from django.db.models import Q
import operator
from .constants import OPERATION_DEFAULT, SORT, LOOKUP_SEP


# class QueryList(list):
#     """A simple list for Querys that allows for easy django qification.  Note
#     that QueryList assumes that it contains only Query objects
#     """

#     def _single_q(self, query):
#         """Returns a q object for a single query object
#         """
#         # If the query is empty, then just make a no-op Q object
#         if not query.path or not query.value:
#             return Q()

#         key = query.django_query

#         # Build query objects for all the values
#         qobjects = (Q(**{key: value}) for value in query.value)

#         # Reduce them all to a single one via 'or'ing them
#         q = reduce(operator.or_, qobjects)

#         # Negate it if neccesary
#         return (~q) if query.negated else q

#     def as_q(self):
#         """get a Q object for all the Query objects stored within
#         """
#         # gather all the Q objects
#         qobjects = (self._single_q(query) for query in self)

#         # Reduce them to a single q object
#         return reduce(operator.and_, qobjects)

#     def as_order(self):
#         """Returns a list of all the sorting directions
#         """
#         orders = []
#         for query in self:
#             if query.direction is not None:
#                 orders.append(query.direction + query.django_path)
#         return orders


class Query(object):
    """The base class for storing parsed queries
    """

    @property
    def django_query(self):
        """A simple property that returns the string used in a django query for
        this object
        """
        return LOOKUP_SEP.join((self.django_path, self.operation))

    @property
    def django_path(self):
        """The django path for the current query lookup
        """
        return LOOKUP_SEP.join(self.path)

    @property
    def direction(self):
        """The sorting direction
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        """Getter for the sorting direction.
        """
        # lowercase it and make sure that its valid
        if value is not None:
            value = value.lower()

        if value not in SORT.keys():
            raise ValueError("Sorting direction must be asc or desc.")

        # Internally, declare ascending order as a '+' and descending order as
        # a '-' to optimize for django's ORM
        self._direction = SORT[value]

    def __init__(self, **kwargs):
        super(Query, self).__init__()

        # Initialize some junk
        self._direction = None

        #! Attribute Path.  This does not include any operations or negation.
        self.path = kwargs.get('path', [])

        #! Operation.  This is the operation being done to the attribute.
        self.operation = kwargs.get('operation', OPERATION_DEFAULT)

        #! Negation.  If the operation has been negated, this is true.
        self.negated = kwargs.get('negated', False)

        #! Sorting direction.  may be 'asc', 'desc', or None if no direction is
        #! specified.
        self.direction = kwargs.get('direction', None)

        #! The value of the operation.  The value may be none if only a sorting
        #! direction was specified.  In this case, do not filter this field
        #! Otherwise, it follows this pattern:
        #! [foo, bar] where foo and bar must be ORed, and the result
        #! ANDed with any other queries, including other queries with the same
        #! name.
        self.value = kwargs.get('value', [])

        #! The next query to be parsed in the chain.  Is none if there are none
        #! next
        self.next = kwargs.get('next', None)

        #! The operation that will be used with the next query in the chain
        self.verb = kwargs.get('verb', operator.and_)

        #! A flag specifying if this is operating on a through table
        self.through = kwargs.get('through', False)


class GroupedQuery(Query):
    """This is a query with specific left and right operands.  It is used with
    grouped queries via parenthesis
    """

    def __init__(self, **kwargs):
        super(GroupedQuery, self).__init__(**kwargs)

        #! The left operand in this grouped query.
        self.left = kwargs.get('left', None)
