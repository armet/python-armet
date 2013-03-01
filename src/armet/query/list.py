# -*- coding: utf-8 -*-
"""The query parsing not-so-state machine
"""
# from cStringIO import StringIO
from query import Query
import operator
from six.moves import cStringIO as StringIO
from collections import Iterable
from itertools import chain
from armet.exceptions import BadRequest
from django.db.models import Q
from .constants import (OPERATIONS, OPERATION_NOT, AND_OPERATOR, OR_OPERATOR,
                        EQUALS, EQUALS_NOT, PATH_SEP, GROUP_START, GROUP_END,
                        EQUALS_SET, VALUE_SEP, TERMINATOR, SORT, SORT_SEP)

COMBINATIONS = {
    AND_OPERATOR: operator.and_,
    OR_OPERATOR: operator.or_,
}


class QueryList(list):

    def __init__(self, querystring, subset=False, negated=False):
        super(QueryList, self).__init__()

        # A reference to the original query string
        self.querystring = querystring

        # Boolean telling us if we're nested
        self.subset = subset

        # Boolean telling us if this was negated
        self.negated = negated

        # Operation for this query
        self.verb = operator.and_

        # Make an iterator out of the query string so that we can pass it
        # to other functions and have it keep its state
        self.parse(iter(querystring))

    def equals_parse(self, q, segiter, *buf):
        # This will likely be expanded in the future for things like >= <= etc.
        for char in chain(buf, segiter):
            if char == EQUALS:
                # We're done parsing the equals sign. break
                return
            elif char == EQUALS_NOT:
                # Encountered a negation, negify the q
                q.negated ^= True
            else:
                # Found an unknown character when trying to parse the equals
                # sign.
                raise BadRequest('Invalid comparison: {}'.format(char))

    def sort_parse(self, segiter):
        # Parse the sorting direction, then proxy to the equals if neccesary
        # Pop an item off the iterator and begin narrowing down the choices

        keys = SORT.keys()

        for iteration, char in enumerate(segiter):
            # downcase the char to make this case insensitive
            char = char.lower()

            if not len(keys):
                # We've run out of possible sorting directions
                raise BadRequest('invalid sorting direction')

            # Use a reversed iterator here so that .remove doesn't throw the
            # internal state of the iterator out of whack.
            for key in reversed(keys):
                if key[iteration] != char:
                    # This isn't a valid sorting direction, remove it
                    keys.remove(key)
                    continue

                if len(key) == iteration + 1:
                    # Found the sorting direction
                    return key

    def segment(self, segment):
        q = Query()

        segiter = iter(segment)
        buf = StringIO()

        for char in segiter:

            if char == SORT_SEP:
                # We're entering the sorting section.  Get the sorting
                # direction
                q.path.append(buf.getvalue())
                buf.truncate(0)
                q.direction = self.sort_parse(segiter)

                if len(q.path) == 1 and q.path[0] == '':
                    raise BadRequest('No filtering parameters passed')

                # Send to the equals parser
                self.equals_parse(q, segiter)

                # Break and go to the value parser
                break

            elif char in EQUALS_SET:
                # Head to the equals parser
                q.path.append(buf.getvalue())
                buf.truncate(0)
                self.equals_parse(q, segiter, char)

                # Break and go to the value parser
                break

            elif char in PATH_SEP:
                # A path separator, push the current stack into the path
                # The nest portion is the sorting direction
                q.path.append(buf.getvalue())
                buf.truncate(0)

                # We're going for another part of the path
                continue

            # No exciting values
            buf.write(char)

        # Write any remaining stuff into the path
        if buf.tell():
            q.path.append(buf.getvalue())

        # Noramlize the path a bit
        try:
            # The keyword 'not' can be the last item in the chain to negify it
            if q.path[-1] == OPERATION_NOT:
                q.negated ^= True
                q.path.pop(-1)

            # The last keyword can be an optional operation
            if q.path[-1] in OPERATIONS:
                q.operation = q.path.pop(-1)

            # Make sure we still have keys that we can use
            if not q.path:
                # Proxy to the exception handler below
                raise IndexError
        except IndexError:
            # We ran out of path items after removing operations and negations
            raise BadRequest('No path specified for {}'.format(segment))

        # Values are not as complicated as the rest of the query set, so just
        # slice em up
        value = ''.join(segiter)
        if value:
            q.value = value.split(VALUE_SEP)

        return q

    def group(self, stringiter):

        string = StringIO()
        for char in stringiter:
            if char == GROUP_END:
                # We're done nesting ourselves, return the cool thing we found
                query = QueryList(string.getvalue(), True)

                # Read ahead to grab the verb
                try:
                    verb = stringiter.next()
                    query.verb = COMBINATIONS[verb]
                except StopIteration:
                    # The iterator is actually over.  do nothing
                    pass

                return query
            else:
                string.write(char)
        raise BadRequest('Missing a closing )')

    def parse(self, querystring):
        """Parse the query string
        """

        string = StringIO()
        for char in querystring:
            # We want to stop reading the query and pass it off to someone
            # when we reach a &, ;, or (
            if char in (AND_OPERATOR, OR_OPERATOR):
                if not string.tell():
                    # The last one was odd, Throw something
                    raise BadRequest('found a {} out of place'.format(char))

                query = self.segment(string.getvalue())
                string.truncate(0)

                self.append(query)

                # Set the query equal to the operation being performed and
                # then continue
                query.verb = COMBINATIONS[char]

            elif char == GROUP_START:
                # See if the last thing was a negation
                if string.getvalue() == EQUALS_NOT:
                    string.truncate(0)
                    negated = True
                else:
                    negated = False

                # TODO: freak out of there was no and or or marker before this
                if string.tell():
                    # There are characters in the buffer, the last one wasn't
                    # the start of a string or &, ;
                    raise BadRequest('Encountered a ( before we should have')

                # Create a grouping query string from this
                query = self.group(querystring)
                # Make note if this needs to be negated
                query.negated = negated

                self.append(query)

            elif char == GROUP_END:
                # We're done here!
                if not self.subset:
                    # But we're not nested.  Panic
                    raise BadRequest('Encountered a ) before we should have')

                self.append(self.segment(string.getvalue()))
                return self

            elif char == TERMINATOR:
                # We've reached the hash string, abort.
                self.append(self.segment(string.getvalue()))
                return self

            else:
                # This isn't a special character, just roll with it
                string.write(char)

        # TODO: throw some nonsense here if the query string ended with a
        # & or ;, because that makes no sense

        if string.tell():
            self.append(self.segment(string.getvalue()))

        return self

    def as_order(self):
        """Returns the sorting direction. Everything inside parenthesis are
        first.
        """
        # Separate everything into 2 queues because parens need to be evaluated
        # first
        parens = (x.as_order() for x in self if isinstance(x, Iterable))
        queries = (x.as_order() for x in self if not isinstance(x, Iterable))

        # Unroll parens since they return a list
        parens = chain(*parens)

        # Make a big list of sorting directions and return them
        return list(x for x in chain(parens, queries) if x)

    def as_q(self):
        """Returns a single q object that represents this QueryList
        """
        q = Q()
        last = operator.and_

        # This is a bit more complicated than reduce can handle
        for item in self:
            q = last(q, item.as_q())
            last = item.verb

        return (~q) if self.negated else q
