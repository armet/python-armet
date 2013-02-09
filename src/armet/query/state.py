# -*- coding: utf-8 -*-
"""The query parsing not-so-state machine
"""
# from cStringIO import StringIO
from query import Query
from collections import deque
import operator
import inspect
from six.moves import cStringIO as StringIO


OPERATIONS = {
    '&': operator.and_,
    ';': operator.or_,
}


class QueryList(list):

    def __init__(self, querystring, subset=False):
        super(QueryList, self).__init__()

        # A reference to the original query string
        self.querystring = deque(querystring)

        # Boolean telling us if we're nested
        self.subset = subset

        # Make an iterator out of the query string so that we can pass it
        # to other functions and have it keep its state
        if not inspect.isgenerator(querystring):
            querystring = iter(querystring)
        self.parse(querystring)

    def sortparse(self, segiter):
        # Parse the sorting direction
        pass

    def segment(self, segment):
        q = Query()

        segment = iter(segment)
        buf = StringIO()

        for char in segment:

            if char in '.:@':
            # A path separator, push the current stack into the path
            # The nest portion is the sorting direction
                q.path.append(buf.getvalue())
                buf.truncate(0)
                if char == ':':
                    # We're entering the sorting section.  Get everything to
                    # the key value separator and
                    q.direction = self.sort_parse(segment)

                elif char == '.':
                    # We're going for another part of the path
                    continue

                # A through table identifier
                elif char == '@':
                    raise NotImplemented('Through support pending')

                continue
            # We're entering the value separator
            if char == '=':
                break
            # Something normal
            buf.write(char)

        # Values are not as complicated as the rest of the query set, so just
        # slice em up
        value = ''.join(segment)
        if value:
            q.value = value.split(',')

        return q

    def group(self, stringiter):

        string = StringIO()
        for char in stringiter:
            if char == ')':
                # We're done nesting ourselves, parse our findings
                string.seek(0)
                print('group parsed: {}'.format(string.read()))
                # We're done nesting ourselves, return the cool thing we found
                string.seek(0)
                query = QueryList(string.read(), True)

                # Read ahead to grab the verb
                try:
                    verb = stringiter.next()
                    query.verb = OPERATIONS[verb]
                except StopIteration:
                    # The iterator is actually over.  do nothing
                    pass

                return query
            else:
                string.write(char)
        print('QueryList.group exited the loop!?  unclosed parens?')
        raise ValueError('Missing a closing )')

    def parse(self, querystring):
        """Parse the query string
        """

        string = StringIO()
        for char in querystring:
            # We want to stop reading the query and pass it off to someone
            # when we reach a &, ;, or (
            if char in ('&', ';'):
                if not string.tell():
                    # The last one was odd, Throw something
                    raise ValueError('found a {} out of place'.format(char))

                query = self.segment(string.getvalue())
                string.truncate(0)

                self.append(query)

                # Set the query equal to the operation being performed and
                # then continue
                query.verb = OPERATIONS[char]

            elif char == '(':
                # TODO: freak out of there was no and or or marker before this
                if string.tell():
                    # There are characters in the buffer, the last one wasn't
                    # the start of a string or &, ;
                    raise Exception('Encountered a ( before we should have')
                # Create a grouping query string from this
                query = self.group(querystring)

                self.append(query)

            elif char == ')':
                # We're done here!
                if not self.subset:
                    # But we're not nested.  Panic
                    raise ValueError('Encountered a ) before we should have')

                self.append(self.segment(string.getvalue()))
                return self

            elif char == '#':
                # We've reached the hash string, abort.
                self.append(self.segment(string.getvalue()))
                return self

            else:
                string.write(char)

        # TODO: throw some nonsense here if the query string ended with a
        # & or ;, because that makes no sense

        if string.tell():
            self.append(self.segment(string.getvalue()))

        return self
