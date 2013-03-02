# -*- coding: utf-8 -*-
"""Constants being used throughout the parser
"""

# Path navigation separator.
PATH_SEP = '.'
# Django's lookup separator
LOOKUP_SEP = '__'

# Operation constants
OPERATION_DEFAULT = 'exact'
OPERATION_NOT = 'not'
# We only support a subset of django's query operations
OPERATIONS = (
    'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'isnull', 'regex',
    'iregex',
)

# Equals items
EQUALS = '='
EQUALS_NOT = '!'

# All the characters that begin a key value separator
EQUALS_SET = EQUALS, EQUALS_NOT

# Logical operators
AND_OPERATOR = '&'
OR_OPERATOR = ';'

# ORable value separators
VALUE_SEP = ','
# The char separating a path from the sorting direction
SORT_SEP = ':'

# Groupers
GROUP_START = '('
GROUP_END = ')'

# Query string terminator
TERMINATOR = '#'

# Through table definitions

# Sorting directions and their corresponding verbs in django
SORT = {
    'asc': '',
    'desc': '-',
}
