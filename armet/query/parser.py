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


class QuerySegmentCombinator(object):
    """
    Represents the combination of 2 query segments `(x=y)&(y=z)`
    """

    def __init__(self, left, right, combinator=operator.and_):
        self.left = left
        self.right = right
        self.combinator = combinator


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


def make_segment(self):
    pass


def reset_stringio(buf):
    # This combination of functions happens way too often in here.
    buf.truncate(0)
    buf.seek(0)


def split_segments(text, closing_paren=False):
    """Return objects representing segments."""
    buf = StringIO()

    # The segments we're building, and the combinators used to combine them.
    # Note that after this is complete, this should be true:
    # len(segments) == len(combinators) + 1
    # Thus we can understand the relationship between segments and combinators
    # like so:
    #  s1 (c1) s2 (c2) s3 (c3) where sN are segments and cN are combination
    # functions.
    # TODO: Figure out exactly where the querystring died and post cool
    # error messages about it.
    segments = []
    combinators = []

    # A flag dictating if the last character we processed was a group.
    # This is used to determine if the next character (being a combinator)
    # is allowed to
    last_group = False

    # The recursive nature of this function relies on keeping track of the
    # state of iteration.  This iterator will be passed down to recursed calls.
    iterator = iter(text)

    for character in iterator:
        if character in COMBINATORS:

            # The string representation of our segment.
            val = buf.getvalue()
            reset_stringio(buf)

            if not last_group and not len(val):
                raise ValueError('Unexpected %s.' % character)

            # When a group happens, the previous value is empty.
            if len(val):
                segments.append(parse_segment(val))

            combinators.append(COMBINATORS[character])

        elif character == constants.GROUP_BEGIN:
            # Recursively go into the next group.

            if buf.tell():
                raise ValueError('Unexpected %s' % character)

            segments.append(split_segments(text, True))

        elif character == constants.GROUP_END:
            # Build the segment for anything remaining, and then combine
            # all the segments.
            val = buf.getvalue()

            # Check for unbalanced parens or an empty thing: foo=bar&();bar=baz
            if not buf.tell() or not closing_paren:
                raise ValueError('Unexpected %s' % character)

            segments.append(parse_segment(val))
            return combine(segments, combinators)

        else:
            buf.write(character)
    else:
        # Check and see if the iterator exited early (unbalanced parens)
        if closing_paren:
            raise ValueError('Expected %s.' % constants.GROUP_END)

    # Everything completed normally, combine all the segments into one
    # and return them.
    return combine(segments, combinators)


def combine(segments, combinators):
    raise NotImplementedError


# All of the equality operations sorted in terms of length, that way we can
# short circuit parse_segment and come up with the longest possible equality
SORTED_EQUALITY = reversed(sorted(constants.OPERATOR_EQUALITIES, key=len))


def parse_segment_(text):
    "we expect foo=bar"

    for equals in SORTED_EQUALITY:
        if equals in text:
            key, value = text.split(equals, 1)  # noqa
            operator = constants.OPERATOR_EQUALITY_MAP[equals]  # noqa
            # TODO: do something with this.
    else:
        # TODO Implement directive-only attributes.
        raise ValueError('Encountered a segment with no equality.')

    # Return something.


def parse_segment(text, combinator=constants.LOGICAL_AND):
    # Initialize a query segment.
    segment = QuerySegment()

    # Construct an iterator over the segment text.
    iterator = iter(text)
    stream = StringIO()

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
