""" A file for filtering
"""

from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.utils.functional import cached_property
from . import exceptions


FILTER_SEPARATOR = '__'
OR_SEPARATOR = ','
FILTER_NOT = 'not'
LIST_CASES = ('in', 'range')
LIST_CASES_EXACT_TWO = ('range',)
DEFAULT_FILTER = 'exact'


class InvalidFilter(Exception):
    """Class for throwing internally when theres a filter error
    """
    def __init__(self, name, message):
        super(InvalidFilter, self).__init__()
        self.name = name
        self.message = message


class Filter(object):
    """docstring for Model"""
    def __init__(self, fields):
        self.fields = fields

    @cached_property
    def terminators(self):
        """The list of restricted query terminators (exact, iexact, eq, etc)
        """
        return [x for x in QUERY_TERMS.keys()]

    def filter(self, iterable, filters):
        """Translates an iterable into a filtered iterable
        """
        raise NotImplemented()

    def can_filter(self, filtermap):
        # Make sure the first field is in the allowable list of fields
        fields = self.fields
        try:
            for idx, field_string in enumerate(filtermap, 1):
                field = fields[field_string]

                # Make sure the field is filterable
                # if not field.filterable:
                #     raise InvalidFilter(
                #         FILTER_SEPARATOR.join(filtermap),
                #         'Filtering is not allowed on {}'.format(filtermap[0]))

                # Navigate to a relation
                if idx < len(filtermap):
                    if field.relation is None:
                        # This is not a relational field
                        raise InvalidFilter(
                            FILTER_SEPARATOR.join(filtermap),
                            '{} is not a related field'.format(field_string))
                    fields = field.relation._fields

        except KeyError as e:
            # Happens when field_string can't be found in the fields lookup
            raise InvalidFilter(
                FILTER_SEPARATOR.join(filtermap),
                '{} is not a valid field'.format(e.message))

    def parse(self, name):
        """Parses filters and checks to see if our filter params are valid.
        Filters that do not appear in the fields list are not valid.  Returns
        a string
        """
        # Slice up the parameter into its components
        items = name.split(FILTER_SEPARATOR)

        # Check to see if our filter ends with a 'not' and slice it off the
        # search query
        if items[-1] == FILTER_NOT:
            items = items[:-1]
            negated = True
        else:
            negated = False

        # Grab the last item and see if its a valid terminator.  Remove valid
        # terminators for the purposes of item lookup
        terminator = items[-1]
        if terminator in self.terminators:
            items = items[:-1]
        else:
            terminator = None

        # Make sure that we're allowed to filter this
        try:
            self.can_filter(items)
        except InvalidFilter as e:
            # can_filter doesn't have access to the entire filter string
            # correct the filter string and re-throw it
            e.name = name
            raise

        # Tack on the terminator again
        if terminator is not None:
            items.append(terminator)

        # We're all good, return the querystring, the verb, and the negation
        return LOOKUP_SEP.join(items), terminator or DEFAULT_FILTER, negated


class Model(Filter):
    """model specific filtering stuff
    """

    def q(self, name, value):
        """Returns a q object for the parameters passed
        """
        qstring, qverb, negated = self.parse(name)
        queries = []
        # Expand the values into an ANDable list of ORs
        values = [x.split(OR_SEPARATOR) for x in value]

        # Special case checking for 'in' and 'range' verbs
        # AND all top level items in the values list, OR all sub-items
        for orable in values:
            # Do some checking for the number of items
            if len(orable) > 1 and qverb in LIST_CASES_EXACT_TWO:
                raise InvalidFilter(
                    name,
                    '{} requires at least two parameters'.filter(qverb))
            # If the verb is in one of the list cases, don't generate a ton of
            # queries, instead just generate one for the array (x__exact=[2,3])
            if qverb in LIST_CASES:
                queries.append(Q(**{qstring: orable}))
            else:
                # Generate a bunch of Q objects instead
                q = [Q(**{qstring: x}) for x in orable]
                queries.append(reduce(lambda x, y: x | y, q))

        # AND all the resulting queries and return them
        return reduce(lambda x, y: x & y, queries)

    def filter(self, iterable, filters):
        # Short circuit if there are no filters
        if not filters:
            return iterable.all()

        # Tidy the filters list
        # filters = self.tidy(filters)
        # Get the list of Q objects
        # queries = [self.q(k, v) for k, v in filters.items()]
        queries = []
        errors = []
        for k, v in filters.items():
            try:
                queries.append(self.q(k, v))
            except InvalidFilter as e:
                # Collect our filtering errors and present them all to the
                # user at the same time
                errors.append(e)
        # If we have any filtering errors, just throw them.
        if errors:
            raise exceptions.BadRequest({e.name: e.message for e in errors})

        # AND all the Q objects and filter the result
        return iterable.filter(reduce(lambda x, y: x & y, queries))
