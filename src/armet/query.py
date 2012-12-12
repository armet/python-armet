# -*- coding: utf-8 -*-
"""
Defines the query parser for Armet
"""

from __future__ import (print_function, unicode_literals, absolute_import,
    division)
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from . import exceptions
import collections


#! Some constants
PARAM_SEP = '&'
KEY_VALUE_SEP = '='
VALUE_SEP = ';'
SORT_SEP = ':'
SORT_VALID = ('asc', 'desc', None)

OPERATION_DEFAULT = 'exact'
OPERATION_NOT = 'not'


class QueryItem(object):
    """Simple structure to wrangle query parameters"""

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
        value = value.lower()
        if value not in SORT_VALID:
            raise ValueError(
                'Sorting direction must be in {}'.format(SORT_VALID))
        self._direction = value

    def __init__(self, **kwargs):
        super(QueryItem, self).__init__()

        # Initialize some junk
        self._direction = None

        #! Attribute Path.  This does not include any operations or negation.
        self.path = kwargs.get('path', None)

        #! Operation.  This is the operation being done to the attribute.
        self.operation = kwargs.get('operation', 'exact')

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
        self.value = kwargs.get('value', None)


class Query(object, collections.Sequence):
    """Query parameter parser.  This behaves like an iterable and returns a
    QueryItem
    """

    def __init__(self, querystring=None):
        super(Query, self).__init__()

        self.parameters = []

        #! Takes one query string to seed the iterable
        if querystring is not None:
            self.add_query(querystring)

    def add_query(self, querystring):
        """Adds a raw querystring to this iterable
        """

        # Break up partitions in the querystring
        segments = querystring.split(PARAM_SEP)

        for segment in segments:
            try:
                # Make a new query and append it to the list
                item = QueryItem()
                self.parameters.append(item)

                # Break up into key value pairs
                key, value = segment.split(KEY_VALUE_SEP)

                # Break up values
                item.value = value.split(VALUE_SEP)

                # Break up key into key and sorting direction
                if SORT_SEP in key:
                    key, item.direction = key.split(SORT_SEP)

                # Break up keys
                keys = key.split(LOOKUP_SEP)

                # Detect negation
                if keys[-1].lower() is OPERATION_NOT:
                    item.negated = True
                    keys = keys[:-1]

                # Detect operation
                operation = keys[-1]
                if keys[-1].lower() in QUERY_TERMS:
                    item.operation = operation
                    keys = keys[-1]

                # Make sure we still have a path to filter by
                if not len(keys):
                    # Delegate to the except down below
                    raise KeyError

                item.path = keys

            except ValueError, KeyError:
                # This will be reached if there was a failure to break
                # up the query into key value paris,
                # or if the query did not include enough parameters
                raise exceptions.BadRequest('Bad query: ' + segment)

    def __len__(self):
        return len(self.parameters)

    def __iter__(self):
        return self.parameters

    def __contains__(self, item):
        return item in self.parameters

    def __getitem__(self, index):
        return self.parameters[index]
