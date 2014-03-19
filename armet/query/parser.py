# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from six.moves import cStringIO as StringIO
import operator
import itertools
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


# Make a reversed suffix map for convenient stringification.
REVERSED_OPERATOR_SUFFIX_MAP = dict(
    (v, k) for k, v in constants.OPERATOR_SUFFIX_MAP.items()
)


class Query(object):
    """Represents a complete query expression.
    """

    def __init__(self, original, parsed):
        # Keep a copy of the original querystring.
        self.original = original
        self.parsed = parsed


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
        self.operator = kwargs.get(
            'operator',
            constants.OPERATOR_MAP[constants.OPERATOR_IEQUAL]
        )

        #! Negation; if this operation has been negated.
        self.negated = kwargs.get('negated', False)

        #! Directives. Directives are a key-value way of specifying commands
        #! on an attribute path.
        self.directives = kwargs.get('directives', [])

        #! Values. Set of values that the attribute path is being checked
        #! against. Only one has to match.
        self.values = kwargs.get('values', [])

    def __repr__(self):
        return str(self)

    def __str__(self):
        """
        Format this query segment in a human-readable representation
        intended for debugging.
        """

        o = StringIO()

        o.write('(')

        if self.negated:
            o.write('not ')

        o.write('.'.join(self.path))

        if self.values:
            o.write(' :%s ' % REVERSED_OPERATOR_SUFFIX_MAP[self.operator])

        o.write(' | '.join(map(lambda x: "'{}'".format(str(x)), self.values)))

        o.write(')')
        return o.getvalue()


class NoopQuerySegment(object):
    """A query segment that doesn't perform an operation.  For the purposes
    of binary and unary combinations, this should be treated as True.
    A NoopQuerySegment should only be encountered when the entire query string
    is missing."""

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "TRUE"


class BinarySegmentCombinator(object):
    """
    Represents the combination of 2 query segments `(x=y)&(y=z)`
    """

    def __init__(self, left, right, operation=operator.and_):
        self.left = left
        self.right = right
        self.operation = operation

    def __repr__(self):
        return str(self)

    def __str__(self):
        combinators = {
            operator.and_: 'AND',
            operator.or_: 'OR'
        }

        return "{} {} {}".format(
            str(self.left),
            combinators[self.operation],
            str(self.right)
        )


class UnarySegmentCombinator(object):
    """
    Represents a unary combination of 2 query segments. `!(x=y)`
    """
    def __init__(self, operand, operation=operator.not_):
        self.operand = operand
        self.operation = operation

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{} {}".format('NOT', self.operand)


def parse(text, encoding='utf8'):
    """Parse the querystring into a normalized form."""

    # Decode the text if we got bytes.
    if isinstance(text, six.binary_type):
        text = text.decode(encoding)

    return Query(text, split_segments(text))


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

    # Detection for exclamation points.  only matters for this situation:
    # foo=bar&!(bar=baz)
    last_negation = False

    for character in iterator:
        if character in COMBINATORS:

            if last_negation:
                buf.write(constants.OPERATOR_NEGATION)

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

            seg = split_segments(iterator, True)

            if last_negation:
                seg = UnarySegmentCombinator(seg)

            segments.append(seg)

            # Flag that the last entry was a grouping, so that we don't panic
            # when the next character is a logical combinator
            last_group = True
            continue

        elif character == constants.GROUP_END:
            # Build the segment for anything remaining, and then combine
            # all the segments.
            val = buf.getvalue()

            # Check for unbalanced parens or an empty thing: foo=bar&();bar=baz
            if not buf.tell() or not closing_paren:
                raise ValueError('Unexpected %s' % character)

            segments.append(parse_segment(val))
            return combine(segments, combinators)

        elif character == constants.OPERATOR_NEGATION and not buf.tell():
            last_negation = True
            continue

        else:
            if last_negation:
                buf.write(constants.OPERATOR_NEGATION)
            if last_group:
                raise ValueError('Unexpected %s' % character)
            buf.write(character)

        last_negation = False
        last_group = False
    else:
        # Check and see if the iterator exited early (unbalanced parens)
        if closing_paren:
            raise ValueError('Expected %s.' % constants.GROUP_END)

        if not last_group:
            # Add the final segment.
            segments.append(parse_segment(buf.getvalue()))

    # Everything completed normally, combine all the segments into one
    # and return them.
    return combine(segments, combinators)


def combine(segments, combinators):
    # We get [a,b,c] in segments and combinators that should be applied as
    # [a(op)b, result(op)c]
    operands = iter(segments)
    operators = iter(combinators)
    first = next(operands)
    reducer = lambda x, y: BinarySegmentCombinator(x, y, next(operators))
    return six.moves.reduce(reducer, operands, first)


def parse_directive(key):
    """
    Takes a key of type (foo:bar) and returns either the key and the
    directive, or the key and None (for no directive.)
    """
    if constants.DIRECTIVE in key:
        return key.split(constants.DIRECTIVE, 1)
    else:
        return key, None


def parse_segment(text):
    "we expect foo=bar"

    if not len(text):
        return NoopQuerySegment()

    q = QuerySegment()

    # First we need to split the segment into key/value pairs.  This is done
    # by attempting to split the sequence for each equality comparison.  Then
    # discard any that did not split properly.  Then chose the smallest key
    # (greedily chose the first comparator we encounter in the string)
    # followed by the smallest value (greedily chose the largest comparator
    # possible.)

    try:
        # import ipdb; ipdb.set_trace()
        # translate into [('=', 'foo=bar')]
        equalities = zip(constants.OPERATOR_EQUALITIES, itertools.repeat(text))
        # Translate into [('=', ['foo', 'bar'])]
        equalities = map(lambda x: (x[0], x[1].split(x[0], 1)), equalities)
        # Remove unsplit entries and translate into [('=': ['foo', 'bar'])]
        # Note that the result from this stage is iterated over twice.
        equalities = list(filter(lambda x: len(x[1]) > 1, equalities))
        # Get the smallest key and use the length of that to remove other items
        key_len = len(min((x[1][0] for x in equalities), key=len))
        equalities = filter(lambda x: len(x[1][0]) == key_len, equalities)

        # Get the smallest value length. thus we have the earliest key and the
        # smallest value.
        op, (key, value) = min(equalities, key=lambda x: len(x[1][1]))
    except ValueError:
        # Only the key exists.  See if there's a directive.
        key, directive = parse_directive(text)
        value = ''
        op = constants.OPERATOR_EQUALITY_FALLBACK
        if directive is None:
            # import ipdb; ipdb.set_trace()
            raise ValueError(
                'Encountered a segment with neither directive nor equality.')

        q.directive = directive

    # Process negation.  This comes in both foo.not= and foo!= forms.
    path = key.split(constants.SEP_PATH)
    last = path[-1]

    # Check for !=
    if last.endswith(constants.OPERATOR_NEGATION):
        last = last[:-1]
        q.negated = not q.negated

    # Check for foo.not=
    if last == constants.PATH_NEGATION:
        path.pop(-1)
        q.negated = not q.negated

    q.values = value.split(constants.SEP_VALUE)

    # Check for suffixed operators (foo.gte=bar).  Prioritize suffixed
    # entries over actual equality checks.
    if path[-1] in constants.OPERATOR_SUFFIXES:

        # The case where foo.gte<=bar, which obviously makes no sense.
        if op not in constants.OPERATOR_FALLBACK:
            raise ValueError(
                'Both path-style operator and equality style operator '
                'provided.  Please provide only a single style operator.')

        q.operator = constants.OPERATOR_SUFFIX_MAP[path[-1]]
        path.pop(-1)
    else:
        q.operator = constants.OPERATOR_EQUALITY_MAP[op]

    if not len(path):
        raise ValueError('No attribute navigation path provided.')

    q.path = path

    return q
