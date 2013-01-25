# -*- coding: utf-8 -*-
"""Constants being used throughout the parser
"""

# Path navigation separator.
PATH_SEP = '.'

# Operation constants
OPERATION_DEFAULT = 'exact'
OPERATION_NOT = 'not'
# We only support a subset of django's query operations
OPERATIONS = (
    'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt', 'lte',
    'startswith', 'istartswith', 'endswith', 'iendswith', 'isnull', 'regex',
    'iregex',
)

# Separators
PARAM_SEP = '&'
KEY_VALUE_SEP = '='
VALUE_SEP = ','
SORT_SEP = ':'

# Sorting directions and their corresponding verbs in django
SORT = {
    'asc': '',
    'desc': '-',
    None: None,
}
