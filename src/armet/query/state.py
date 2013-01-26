# -*- coding: utf-8 -*-
"""The query parsing not-so-state machine
"""
from cStringIO import StringIO
from query import Query
from collections import deque
import operator
import inspect


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

    def segment(self, stringio):
        stringio.seek(0)
        print('got a segment: {}'.format(stringio.read()))
        return Query()

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

                query = self.segment(string)
                string = StringIO()

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

                self.append(self.segment(string))
                return self

            else:
                string.write(char)

        # TODO: throw some nonsense here if the query string ended with a
        # & or ;, because that makes no sense

        # if not string.tell():
        #     # It ended with a & or ;
        #     raise Exception('Queries cannot end with & or ;')

        if string.tell():
            self.append(self.segment(string))

        return self
