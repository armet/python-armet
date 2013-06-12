# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from six.moves import cStringIO as StringIO
import operator
from itertools import chain
from . import constants


#! Operation to combinator map.
COMBINATORS = {
    constants.LOGICAL_AND: operator.and_,
    constants.LOGICAL_OR: operator.or_}


#! Set of characters that begin an operator.
OPERATOR_BEGIN_CHARS = set(x[0] for _, x in constants.OPERATORS if x)


#! Dictionary of operator symbols to operators.
OPERATOR_SYMBOL_MAP = dict((v, k) for k, v in constants.OPERATORS if v)


class Query(object):
    """Represents a complete query expression.
    """

    def __init__(self, text):
        #! The various query segments.
        self.segments = []

        # Parse the query string.
        self._parse(text)

    def _parse(self, text):
        """Parse the querystring into a normalized form."""
        # Iterate through the characters in the query string; one-by-one
        # in order to perform one-pass parsing.
        stream = StringIO()
        for character in text:

            # We want to stop reading the query and pass it off to someone
            # when we reach a logical or grouping operator.
            if character in (constants.LOGICAL_AND, constants.LOGICAL_OR):

                if not stream.tell():
                    # There is no content in the stream; a logical operator
                    # was found out of place.
                    raise ValueError('Found `{}` out of place'.format(
                        character))

                # Parse the segment up till the combinator
                segment = QuerySegment(stream.getvalue(), character)
                self.segments.append(segment)
                stream.truncate(0)

            else:
                # This isn't a special character, just roll with it.
                stream.write(character)

        # TODO: Throw some nonsense here if the query string ended with a
        # & or ;, because that makes no sense.

        if stream.tell():
            # Append the remainder of the query string.
            self.segments.append(QuerySegment(stream.getvalue()))

    def __str__(self):
        """Format the query for debugging purposes.
        """

        o = StringIO()
        for index, segment in enumerate(self.segments):
            o.write('(')
            o.write('"{}"'.format('.'.join(segment.path)))
            o.write(' :{} '.format(segment.operator))

            for jndex, value in enumerate(segment.values):
                if jndex:
                    o.write(' OR ')

                o.write("'{}'".format(value))

            o.write(')')

            if (index + 1) < len(self.segments):
                comb = 'AND' if segment.combinator == operator.and_ else 'OR'
                o.write(' {} '.format(comb))

        return o.getvalue()


class QuerySegment(object):
    """
    Represents a single query segment with a subject path (`x.a.g`),
    an operator (`=` or `<=`), optional directives (`sort`), and
    a set of values (`5,12,56`).
    """

    def __init__(self, text, combinator=constants.LOGICAL_AND):
        #! Path to the attribute being tested (as a list of segments).
        self.path = []

        #! This is the operator that is being applied to the attribute path.
        self.operator = constants.OPERATOR_IEQUAL

        #! Negation; if this operation has been negated.
        self.negated = False

        #! Directives. Directives are a key-value way of specifying commands
        #! on an attribute path.
        self.directives = []

        #! Values. Set of values that the attribute path is being checked
        #! against. Only one has to match.
        self.values = []

        #! The combinator that is used to combine this and the next
        #! query.
        self.combinator = COMBINATORS[combinator]

        # Parse the text and determine the values of the segment.
        self._parse(text)

    def _parse(self, text):
        # Construct an iterator over the segment text.
        iterator = iter(text)
        stream = StringIO()

        # Iterate through the characters in the segment; one-by-one
        # in order to perform one-pass parsing.
        for character in iterator:

            if character in OPERATOR_BEGIN_CHARS:
                # Found an operator; pull out what we can.
                self._parse_operator(chain(character, iterator))

                # We're done here; go to the value parser
                break

            if character == constants.SEP_PATH:
                # A path separator, push the current stack into the path
                self.path.append(stream.getvalue())
                stream.truncate(0)

                # Keep checking for more path segments.
                continue

            # Append the text to the stream
            stream.write(character)

        # Write any remaining information into the path.
        self.path.append(stream.getvalue())

        # Attempt to normalize the path.
        try:
            # The keyword 'not' can be the last item which
            # negates this query.
            if self.path[-1] == constants.NEGATION[0]:
                self.negated = not self.negated
                self.path.pop(-1)

            # The last keyword can explicitly state the operation; in which
            # case the operator symbol **must** be `=`.
            if self.path[-1] in OPERATOR_SYMBOL_MAP.values():
                if self.operator is not constants.OPERATOR_IEQUAL[0]:
                    raise ValueError(
                        'Explicit operations must use the `=` symbol.')

                self.operator = self.path.pop(-1)

            # Make sure we still have a path left.
            if not self.path:
                raise IndexError()

        except IndexError:
            # Ran out of path items after removing operations and negation.
            raise ValueError('No path specified in {}'.format(text))

        # Values are not complicated (yet) so just slice and dice
        # until we get a list of possible values.
        self.values = ''.join(iterator)
        if self.values:
            self.values = self.values.split(constants.SEP_VALUE)

    def _parse_operator(self, iterator):
        """Parses the operator (eg. '==' or '<')."""
        stream = StringIO()
        for character in iterator:
            if character == constants.NEGATION[0]:
                if stream.tell():
                    # Negation can only occur at the start of an operator.
                    raise ValueError('Unexpected negation.')

                # We've been negated.
                self.negated = not self.negated
                continue

            # Expand the operator
            stream.write(character)

            if stream.getvalue() in OPERATOR_SYMBOL_MAP:
                # We're an operator.
                break

        # Set the found operator
        self.operator = OPERATOR_SYMBOL_MAP[stream.getvalue()]
