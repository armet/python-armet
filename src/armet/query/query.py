# -*- coding: utf-8 -*-
"""
Defines the query parser for Armet
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.db.models import Q
import operator
from itertools import izip
from .constants import OPERATION_DEFAULT, SORT, LOOKUP_SEP


class Query(object):
    """The base class for storing parsed queries
    """
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

        #! The operation that will be used with the next query in the chain
        self.verb = kwargs.get('verb', operator.and_)

        #! A flag specifying if this is operating on a through table
        self.through = kwargs.get('through', False)

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
    def django_direction(self):
        """Django's internal version of the sorting direction
        """
        return self._direction

    @property
    def direction(self):
        """Getter sorting direction.  This shouldn't be called that often
        """
        direction = self._direction
        if direction is not None:
            # Invert the sorting dictionary
            sort = dict(izip(SORT.itervalues(), SORT.iterkeys()))

            direction = sort[direction]
        return direction

    @direction.setter
    def direction(self, value):
        """Setter for the sorting direction.
        """
        # Short circuit for unsetting the direction
        if value is None:
            self._direction = None
            return

        # Make sure that the sorting direction is valid
        # lowercase it and make sure that its valid
        value = value.lower()

        if value not in SORT.keys():
            raise ValueError("Sorting direction must be asc or desc.")

        # Internally, declare ascending order as a '+' and descending order as
        # a '-' to optimize for django's ORM
        self._direction = SORT[value]

    def as_q(self):
        """Make a django q object out of ourselves
        """
        if not self.path or not self.value:
            # We don't have both keys and values, so just return an empty thing
            return Q()

        key = self.django_query

        # Build query objects for all the values
        qobjects = (Q(**{key: value}) for value in self.value)

        # Reduce them all to a single one
        q = reduce(operator.or_, qobjects)

        # Return and negate
        return (~q) if self.negated else q

    def as_order(self):
        """Returns the sorting direction (the same as self.django_direction)
        """
        if self.django_direction:
            return self.django_direction + self.django_path
