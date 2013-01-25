# -*- coding: utf-8 -*-
# Relay the following imports for armet
from query import QueryList, Query
from armet import exceptions
from constants import (PATH_SEP, OPERATION_NOT, VALUE_SEP, PARAM_SEP,
    KEY_VALUE_SEP, SORT_SEP, OPERATIONS)


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
