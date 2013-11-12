# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


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

#! Operators
OPERATORS = (
    OPERATOR_EQUAL,
    OPERATOR_IEQUAL,
    OPERATOR_LT,
    OPERATOR_LTE,
    OPERATOR_GT,
    OPERATOR_GTE,
    OPERATOR_REGEX,
    OPERATOR_ISNULL,
    OPERATOR_IN)

#! Negation
NEGATION = ('not', '!')

#! Logical
LOGICAL_AND = '&'
LOGICAL_OR = ';'

#! Path separator
SEP_PATH = '.'

#! Value separator
SEP_VALUE = ','

#! Directive initiator
DIRECTIVE = ':'

#! Grouping characters
GROUP_BEGIN = '('
GROUP_END = ')'
