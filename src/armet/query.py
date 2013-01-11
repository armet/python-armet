# -*- coding: utf-8 -*-
"""
Defines the query parser for Armet
"""

from __future__ import (print_function, unicode_literals, absolute_import,
    division)
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from . import exceptions
import collections

#! django constants
DJANGO_ASC = '+'
DJANGO_DESC = '-'

#! Some constants
OPERATION_DEFAULT = 'exact'
OPERATION_NOT = 'not'
PARAM_SEP = '&'
KEY_VALUE_SEP = '='
VALUE_SEP = ';'
SORT_SEP = ':'
SORT_ASC = 'asc'
SORT_DESC = 'desc'
SORT_DEFAULT = None
SORT_VALID = (SORT_ASC, SORT_DESC, None)


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
        if value is not None:
            value = value.lower()

        if value not in SORT_VALID:
            raise ValueError(
                "Sorting direction must be {} or {}.".format(
                    SORT_ASC,
                    SORT_DESC,
                )
            )

        # Internally, declare ascending order as a '+' and descending order as
        # a '-' to optimize for django's ORM
        if value == SORT_ASC:
            self._direction = DJANGO_ASC
        elif value == SORT_DESC:
            self._direction = DJANGO_DESC
        else:
            self._direction = None

    def __init__(self, **kwargs):
        super(QueryItem, self).__init__()

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

    item = QueryItem()


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

        # Break up keys
        keys = key.split(LOOKUP_SEP)

        # Detect negation
        if keys[-1].lower() == OPERATION_NOT:
            item.negated = True
            keys = keys[:-1]

        # Detect operation
        operation = keys[-1]
        if keys[-1].lower() in QUERY_TERMS:
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
    """Query parameter parser.  Returns a list of QueryItems.
    """
    # Break up partitions in the querystring
    segments = querystring.split(PARAM_SEP)

    return [parse_segment(x) for x in segments]
