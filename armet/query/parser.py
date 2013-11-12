# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from six.moves import cStringIO as StringIO
import operator
import collections
from itertools import chain
from . import constants


#! Operation to combinator map.
COMBINATORS = {
    constants.LOGICAL_AND: operator.and_,
    constants.LOGICAL_OR: operator.or_}


#! Set of characters that begin an operator.
OPERATOR_BEGIN_CHARS = set(x[0] for _, x in constants.OPERATORS if x)
OPERATOR_BEGIN_CHARS.add(constants.NEGATION[1])

#! Dictionary of operator symbols to operators.
OPERATOR_SYMBOL_MAP = dict((v, k) for k, v in constants.OPERATORS if v)


#! List of operator keywords.
OPERATOR_KEYWORDS = set(k for k, _ in constants.OPERATORS)


class Query(collections.Sequence):
    """Represents a complete query expression.
    """

    def __init__(self, segments=None):
        #! The various query segments.
        self.segments = [] if segments is None else segments

    def __getitem__(self, index):
        return self.segments[index]

    def __len__(self):
        return len(self.segments)

    def __repr__(self):
        return str(self)

    def __str__(self):
        o = StringIO()

        o.write('(')

        for index, segment in enumerate(self):

            o.write(str(segment))

            if index + 1 < len(self):
                comb = '&' if segment.combinator == operator.and_ else '|'
                o.write(' {} '.format(comb))

        o.write(')')

        return o.getvalue()


def parse(text, encoding='utf8'):
    """Parse the querystring into a normalized form."""
    # Initialize the query object.
    query = Query()

    # Decode the text if we got bytes.
    if isinstance(text, six.binary_type):
        text = text.decode(encoding)

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
            segment = parse_segment(stream.getvalue(), character)
            query.segments.append(segment)
            stream.truncate(0)
            stream.seek(0)

        else:
            # This isn't a special character, just roll with it.
            stream.write(character)

    # TODO: Throw some nonsense here if the query string ended with a
    # & or ;, because that makes no sense.

    if stream.tell():
        # Append the remainder of the query string.
        query.segments.append(parse_segment(stream.getvalue()))

    # Return the constructed query object.
    return query


class QuerySegment(object):
    """
    Represents a single query segment with a subject path (`x.a.g`),
    an operator (`=` or `<=`), optional directives (`sort`), and
    a set of values (`5,12,56`).
    """

    def __init__(self, **kwargs):
        #! Path to the attribute being tested (as a list of segments).
        self.path = kwargs.get('path', [])

        #! This is the operator that is being applied to the attribute path.
        self.operator = kwargs.get('operator', constants.OPERATOR_IEQUAL[0])

        #! Negation; if this operation has been negated.
        self.negated = kwargs.get('negated', False)

        #! Directives. Directives are a key-value way of specifying commands
        #! on an attribute path.
        self.directives = kwargs.get('directives', [])

        #! Values. Set of values that the attribute path is being checked
        #! against. Only one has to match.
        self.values = kwargs.get('values', [])

        #! The combinator that is used to combine this and the next
        #! query.
        self.combinator = kwargs.get('combinator', operator.and_)

    def __repr__(self):
        return str(self)

    def __str__(self):
        """
        Format this query segment in a human-readable representation
        intended for debugging.
        """

        o = StringIO()

        if self.negated:
            o.write('not ')

        o.write('.'.join(self.path))

        if self.values:
            o.write(' :%s ' % self.operator)

        o.write(' | '.join(map(repr, self.values)))
        return o.getvalue()


def _parse_operator(segment, iterator):
    """Parses the operator (eg. '==' or '<')."""
    stream = StringIO()
    for character in iterator:
        if character == constants.NEGATION[1]:
            if stream.tell():
                # Negation can only occur at the start of an operator.
                raise ValueError('Unexpected negation.')

            # We've been negated.
            segment.negated = not segment.negated
            continue

        if (stream.getvalue() + character not in OPERATOR_SYMBOL_MAP and
                stream.getvalue() + character not in OPERATOR_BEGIN_CHARS):
            # We're no longer an operator.
            break

        # Expand the operator
        stream.write(character)

    # Check for existance.
    text = stream.getvalue()
    if text not in OPERATOR_SYMBOL_MAP:
        # Doesn't exist because of a mis-placed negation in the middle
        # of the path.
        raise ValueError('Unexpected negation.')

    # Set the found operator.
    segment.operator = OPERATOR_SYMBOL_MAP[text]

    # Return the remaining characters.
    return chain(character, iterator)


def parse_segment(text, combinator=constants.LOGICAL_AND):
    # Initialize a query segment.
    segment = QuerySegment()

    # Construct an iterator over the segment text.
    iterator = iter(text)
    stream = StringIO()

    # Iterate through the characters in the segment; one-by-one
    # in order to perform one-pass parsing.
    for character in iterator:

        if (character == constants.NEGATION[1]
                and not stream.tell() and not segment.path):
            # We've been negated.
            segment.negated = not segment.negated
            continue

        if character in OPERATOR_BEGIN_CHARS:
            # Found an operator; pull out what we can.
            iterator = _parse_operator(segment, chain(character, iterator))

            # We're done here; go to the value parser
            break

        if character == constants.SEP_PATH:
            # A path separator, push the current stack into the path
            segment.path.append(stream.getvalue())
            stream.truncate(0)
            stream.seek(0)

            # Keep checking for more path segments.
            continue

        # Append the text to the stream
        stream.write(character)

    # Write any remaining information into the path.
    segment.path.append(stream.getvalue())

    # Attempt to normalize the path.
    try:
        # The keyword 'not' can be the last item which
        # negates this query.
        if segment.path[-1] == constants.NEGATION[0]:
            segment.negated = not segment.negated
            segment.path.pop(-1)

        # The last keyword can explicitly state the operation; in which
        # case the operator symbol **must** be `=`.
        if segment.path[-1] in OPERATOR_KEYWORDS:
            if segment.operator != constants.OPERATOR_IEQUAL[0]:
                raise ValueError(
                    'Explicit operations must use the `=` symbol.')

            segment.operator = segment.path.pop(-1)

        # Make sure we still have a path left.
        if not segment.path:
            raise IndexError()

    except IndexError:
        # Ran out of path items after removing operations and negation.
        raise ValueError('No path specified in {}'.format(text))

    # Values are not complicated (yet) so just slice and dice
    # until we get a list of possible values.
    segment.values = ''.join(iterator)
    if segment.values:
        segment.values = segment.values.split(constants.SEP_VALUE)

    # Set the combinator.
    segment.combinator = COMBINATORS[combinator]

    # Return the constructed query segment.
    return segment
