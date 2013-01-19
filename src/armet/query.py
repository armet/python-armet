# -*- coding: utf-8 -*-
"""
Defines the query parser for Armet
"""

from __future__ import (print_function, unicode_literals, absolute_import,
    division)
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models import Q
from . import exceptions
import operator

#! Some constants
PATH_SEP = LOOKUP_SEP
OPERATION_DEFAULT = 'exact'
OPERATION_NOT = 'not'
# We only support a subset of django's query operations
OPERATIONS = (
    'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'isnull', 'regex',
    'iregex',
)
PARAM_SEP = '&'
KEY_VALUE_SEP = '='
VALUE_SEP = ';'
SORT_SEP = ':'

#! Sorting directions and their corresponding verbs in django
SORT = {
    'asc': '',
    'desc': '-',
    None: None,
}
# SORT_ASC =
# SORT_DESC =
# SORT_RAND =
# SORT_DEFAULT =
# SORT_VALID = (SORT_ASC, SORT_DESC, SORT_RAND, None)


class QueryList(list):
    """A simple list for Querys that allows for easy django qification.  Note
    that QueryList assumes that it contains only Query objects
    """

    def _single_q(self, query):
        """Returns a q object for a single query object
        """
        # If the query is empty, then just make a no-op Q object
        if not query.path or not query.value:
            return Q()

        key = query.django_query

        # Build query objects for all the values
        qobjects = (Q(**{key: value}) for value in query.value)

        # Reduce them all to a single one via 'or'ing them
        q = reduce(operator.or_, qobjects)

        # Negate it if neccesary
        return (~q) if query.negated else q

    def as_q(self):
        """get a Q object for all the Query objects stored within
        """
        # gather all the Q objects
        qobjects = (self._single_q(query) for query in self)

        # Reduce them to a single q object
        return reduce(operator.and_, qobjects)

    def as_order(self):
        """Returns a list of all the sorting directions
        """
        orders = []
        for query in self:
            if query.direction is not None:
                orders.append(query.direction + query.django_path)
        return orders


class QueryList(collections.Sequence):
    """A simple query list that implements a Q function for django qification.
    """


class Query(object):
    """Simple structure to wrangle query parameters"""

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
    def direction_set(self, value):
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


def parse_segment(segment):
    """an individual query segment parser.
    """

    item = Query()

    try:
        # Break up into key value pairs
        try:
            key, value = segment.split(KEY_VALUE_SEP)
        except ValueError:
            # There was a problem unpacking the tuple, see if we have
            # a separator at all
            if KEY_VALUE_SEP in segment:
                # There was more than one equals sign, delegate to the
                # exception below
                raise
            # No value, so use an empty array
            key = segment
            item.value = []

        else:
            # Break up values if we didn't run into problems above
            item.value = value.split(VALUE_SEP)

        # Break up key into key and sorting direction
        if SORT_SEP in key:
            key, item.direction = key.split(SORT_SEP)

            # Sorting without a property to sort via is an invalid operation
            if not key and item.direction is not None:
                raise KeyError

        # Break up keys
        keys = key.split(PATH_SEP)

        # Detect negation
        if keys[-1].lower() == OPERATION_NOT:
            item.negated = True
            keys = keys[:-1]

        # Detect operation
        operation = keys[-1]
        if keys[-1].lower() in OPERATIONS:
            item.operation = operation
            keys = keys[:-1]

        # Make sure we still have a path to filter by
        if not len(keys):
            # Delegate to the except down below
            raise KeyError

        item.path = keys

    except (ValueError, KeyError):
        # This will be reached if there was a failure to break
        # up the query into key value paris,
        # or if the query did not include enough parameters
        raise exceptions.BadRequest('Bad query: ' + segment)

    # All went well, return the item
    return item


def parse(querystring):
    """Query parameter parser.  Returns a list of Querys.
    """
    # Break up partitions in the querystring
    segments = querystring.split(PARAM_SEP)

    return QueryList(parse_segment(x) for x in segments)
