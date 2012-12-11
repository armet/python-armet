Filtering
*********

FILTER SEPERATOR
================
The filter seperator, "`__`", seperates the filter and other options you
can use in a query set.

Example::

    http://www.example.com/api/poll?id__gt=4

This will give you all results where the id is greater than 4.

Not Seperator
-------------

Example::

    http://www.example.com/api/poll?id__gt__not=4

This will give you all results where the id is NOT greater than 4. All results
will be from ids less than or equal to 4.

Filters List
------------

The following filters are supported, taken from the django standard::


    exact - Exact match.
    iexact - Case insensitive exact.
    contains - Containment test.
    icontains - Case insensitive contains
    gt - Greater than
    gte - Greater than or equal
    lt - Less than
    lte - Less than or equal
    startswith - Match starts with
    istartswith - Case insensitive startswith
    endswith - Match ends with
    iendswith - Case insensitive endswith
    year
    month
    day
    week_day
    isnull - Returns null matches
    search
    regex - Perform regex, returns a match
    iregex - Case insensitive regex.

All filters can be followed by the not operator for negation. The default
filter is exact.

OR SEPERATOR
============

The OR seperator, a simple semi-colon, is used to search for many values in a
query search.

Example::

    http://www.example.com/api/poll?id__contains=3,5

This would return an id if the id contains 3 OR the id contains 5.
