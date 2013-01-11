Query Parameters
****************

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

Operation List
--------------

The following filters operation are supported, taken from the django standard::


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
    isnull - Returns null matches
    regex - Perform regex, returns a match
    iregex - Case insensitive regex.

Filters without an operation default to an `exact` operation

All filters can be followed by the not operator for negation. The default
filter is exact.


COMBINING FILTERS
=================

And Separator
-------------

Query parameters separated by an ampersand (`&`) will be combined when
filtering responses.

Example::

    http://www.example.com/api/choice?votes__gte=4&votes__lte=10

This will returns all choices that have at least 4 votes, but no more than 10
votes.

Or Separator
------------

The OR seperator, a simple semi-colon, is used to search for many values in a
query search.

Example::

    http://www.example.com/api/poll?id__contains=3,5

This would return an id if the id contains 3 OR the id contains 5.

Multiple Separators
------------------

When both AND and OR separators are used in a single query, OR parameters have
higher precedence than AND parameters

Example::

    http://www.example.com/api/choice?votes__gte=4&choice_text=foo;bar

This will return choices with choice_text of either foo or bar and with at
least 4 votes.  However, order of evaluation is not guaranteed.  It may be
easier to visualize using python code:

.. code:: python
    def is_included_in_response(model):
        if model.votes >= 4 and (model.choice_text in ['foo', 'bar']):
            return True
        else:
            return False

Query parameters may be specified multiple times without clobbering

Example::

    http://www.example.com/api/choice?choice_text__contains=foo&choice_text__contains=bar&votes__gte=4

This will return all choices with choice text contains both 'foo' and 'bar' and
with at least 4 votes.  It may be easier to visualize using python code:

.. code:: python
    def is_include_in_response(model):
        if model.votes >= 4 \
                and 'foo' in model.choice_text \
                and 'bar' in model.choice_text:
            return True
        else:
        return False


SORTING
=======

Responses may have arbirary sorting associated with them by attaching the sort
direction to the parameter name: `asc` for ascending order, and `desc` for
descending order

Example:

    http://www.example.com/api/choice?choice_text:asc

This will sort your choices in ascending order via the 'choice_text' parameter.


Sorted parameters can be combined with filtering as well for convenience.

Example:

    http://www.example.com/api/choice?choice_text__contains:desc=foo

This will filter based on choices that have 'foo' in the choice_text and sort
them in descending order.
