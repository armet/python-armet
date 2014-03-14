# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
import re


#! Equality
OPERATOR_EQUAL = 'exact', '=='

#! Case-insensitve equality
OPERATOR_IEQUAL = 'iexact', '='

#! Less than
OPERATOR_LT = 'lt', '<'

#! Less than or equal to
OPERATOR_LTE = 'lte', '<='

#! Greater than
OPERATOR_GT = 'gt', '>'

#! Greater than or equal to
OPERATOR_GTE = 'gte', '>='

#! Regular expression match
OPERATOR_REGEX = 'regex', '*='

#! Null test
OPERATOR_ISNULL = 'isnull', None

#! In-collection test
OPERATOR_IN = 'in', None

#! Operator map relating operations to python operations.
OPERATOR_MAP = {
    OPERATOR_EQUAL: operator.eq,
    OPERATOR_IEQUAL: lambda x, y: x.lower() == y.lower(),
    OPERATOR_LT: operator.lt,
    OPERATOR_LTE: operator.le,
    OPERATOR_GT: operator.gt,
    OPERATOR_GTE: operator.ge,
    OPERATOR_REGEX: lambda x, y: re.search(y, x),
    OPERATOR_ISNULL: lambda x: x is None,
    OPERATOR_IN: operator.contains,
}

#! Operator set containing all operators.
OPERATORS = set(OPERATOR_MAP.keys())

#! Operators restricted to suffixed paths (foo.gte=bar)
OPERATOR_SUFFIXES = set(filter(None, map(operator.itemgetter(0), OPERATORS)))

#! Operators restricted to equality comparators (foo>=bar)
OPERATOR_EQUALITIES = set(filter(None, map(operator.itemgetter(1), OPERATORS)))

#! Operator map limited to suffixed paths {"gte": operator.ge}
OPERATOR_SUFFIX_MAP = dict(
    filter(operator.itemgetter(0),
           map(lambda x: (x[0][0], x[1]),
               OPERATOR_MAP.items())))

#! Operator map limited to equality checks {">=": operator.ge}
OPERATOR_EQUALITY_MAP = dict(
    filter(operator.itemgetter(0),
           map(lambda x: (x[0][1], x[1]),
               OPERATOR_MAP.items())))

#! Negation
NEGATION = ('not', '!')

#! Logical
LOGICAL_AND = '&'
LOGICAL_OR = ';'

#! Equality map relating operations with python functions.
# Note the missing regex comparison and logical comparisons translate to
# bitwise.  This is because most ORMs overload & and | instead of `and`
# and `or`, because you can't really overload those.
PYTHON_MAP = {
    NEGATION: operator.neg,
    (LOGICAL_AND,): operator.and_,
    (LOGICAL_OR,): operator.or_,
}
PYTHON_MAP.update(OPERATOR_MAP)

#! Path separator
SEP_PATH = '.'

#! Value separator
SEP_VALUE = ','

#! Directive initiator
DIRECTIVE = ':'

#! Grouping characters
GROUP_BEGIN = '('
GROUP_END = ')'
