""" A file for filtering
"""

from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.utils.functional import cached_property
from django.forms import ValidationError
from . import exceptions


FILTER_SEPARATOR = '__'
OR_SEPARATOR = ','
FILTER_NOT = 'not'
LIST_CASES = ('in', 'range')
LIST_CASES_EXACT_TWO = 'range',
DEFAULT_FILTER = 'exact'


class FilterError(Exception):
    """Class for throwing internally when theres a filter error
    """
    def __init__(self, name, message):
        self.name = name
        self.message = message
        super(Exception, self).__init__()


class FilterAction(object):
    """Collection of information about a particular filter.  Can be used later
    to build the Q object
    """

    def __init__(self, **kwargs):
        # Name of the filter as passed by the user
        self.original_name = ''

        # Name of the filter, after the 'not' has been removed
        self.name = ''

        # Values for this filter.  Implemented as a list of lists.  The outer
        # list must be ANDed together, and the inner list must be ORed
        # together.
        self.values = []

        # Boolean for when the filter has been negated
        self.negated = False

        # Field reference to the field that will actually get filtered for this
        self.field = None

        # Verb (exact, equals, in, etc) that will be run on this filter
        self.verb = ''

        keys = self.__dict__.keys()
        for x in kwargs:
            if x in keys:
                setattr(self, x, kwargs[x])


class Filter(object):
    """docstring for Model"""
    def __init__(self, fields):
        # Simple reference to the field list to start from
        self.fields = fields

        # Name is the filter parameter passed in the url, and value is a
        # FilterAction
        self.filters = {}

    @cached_property
    def terminators(self):
        """The list of restricted query terminators (exact, iexact, eq, etc)
        """
        return [x for x in QUERY_TERMS.keys()]

    def filter(self, iterable, filters):
        """Translates an iterable into a filtered iterable
        """
        raise exceptions.NotImplemented({
            'error':
            'Filtering on this resource is not implemented'})

    def can_filter(self, filtermap):
        # Make sure the first field is in the allowable list of fields
        fields = self.fields
        try:
            for idx, field_string in enumerate(filtermap, 1):
                field = fields[field_string]

                # Make sure the field is visible (not blacklisted)
                if not field.visible:
                    raise FilterError(
                        FILTER_SEPARATOR.join(filtermap),
                        '{} is not a valid field'.format(field_string))

                # Make sure the field is filterable
                if not field.filterable:
                    raise FilterError(
                        FILTER_SEPARATOR.join(filtermap),
                       'Filtering is not allowed on {}'.format(filtermap[0]))

                # Navigate to a relation
                if idx < len(filtermap):
                    if field.relation is None:
                        # This is not a relational field
                        raise FilterError(
                            FILTER_SEPARATOR.join(filtermap),
                            '{} is not a related field'.format(field_string))
                    fields = field.relation.fields

        except KeyError as e:
            # Happens when field_string can't be found in the fields lookup
            raise FilterError(
                FILTER_SEPARATOR.join(filtermap),
                '{} is not a valid field'.format(e.message))

        return field

    def pythonify(self, item, action):
        """Pythonifys item according to action
        """
        try:
            return action.field.clean(item)
        except ValidationError as e:
            # The field was unable to parse this thing  Raise a filter error
            raise FilterError(action.original_name, e.messages)

    def parse(self, name, value):
        # Parse the name
        action = self.parse_name(name)

        # Parse the values
        self.filters[name] = self.parse_value(value, action)

    def parse_value(self, values, action):
        """ Takes a list of values, parses them, pythonifys them, and sticks em
        in the action.
        """
        for v in values:
            # Separate the values and pythonify them
            items = [self.pythonify(x, action) for x in v.split(OR_SEPARATOR)]

            # Add them to the list of values
            action.values.append(items)

        return action

    def parse_name(self, name):
        """Parses filters and checks to see if our filter params are valid.
        Filters that do not appear in the fields list are not valid.  Returns
        a string
        """
        # Create a FilterAction object and start populating it
        action = FilterAction(original_name=name)

        # Slice up the parameter into its components
        items = name.split(FILTER_SEPARATOR)

        # Check to see if our filter ends with a 'not' and slice it off the
        # search query
        if items[-1] == FILTER_NOT:
            items = items[:-1]
            action.negated = True
        else:
            action.negated = False

        action.name = LOOKUP_SEP.join(items)
        # Grab the last item and see if its a valid terminator.  Remove valid
        # terminators for the purposes of item lookup
        terminator = items[-1]
        if terminator in self.terminators:
            items = items[:-1]
            action.verb = terminator
        else:
            terminator = None
            action.verb = DEFAULT_FILTER

        # Make sure that we're allowed to filter this
        try:
            action.field = self.can_filter(items)
        except FilterError as e:
            # can_filter doesn't have access to the entire filter string
            # correct the filter string and re-throw it
            e.name = name
            raise e

        # Tack on the terminator again
        if terminator is not None:
            items.append(terminator)

        # We're all good, return the action
        return action
        return LOOKUP_SEP.join(items), terminator or DEFAULT_FILTER, negated


class Model(Filter):
    """model specific filtering stuff
    """

    def q(self):
        """Returns a q object for the parameters passed
        """
        # self.filters contains the list of FilterObjects
        # OR inner ones, AND outer ones.
        queries = []
        for f_action in self.filters.values():
            values = f_action.values
            query = []
            for orable in values:
                # this list must be 'or'ed
                # Verify that special case actions have the right number of values
                if len(orable) > 1 and f_action.verb in LIST_CASES_EXACT_TWO:
                    raise InvalidFilter(
                        name,
                        '{} requires at least two parameters'.filter(
                            f_action.verb))

                # Do special case list building for filters that take an iterable
                # instead of a flat value
                if f_action.verb in LIST_CASES:
                    orable = [orable]

                # Make Q objects out of everything, and OR them
                inner = [Q(**{f_action.name: v}) for v in orable]
                query.append(reduce(lambda x, y: x | y, inner))

            # AND the outer list
            q = reduce(lambda x, y: x & y, query)

            # Not them if needed
            if f_action.negated:
                q = ~q

            queries.append(q)

        # AND all Q objects in the list
        return reduce(lambda x, y: x & y, queries)

    def filter(self, iterable, filters):
        # Short circuit if there are no filters
        if not filters:
            return iterable.all()

        queries = []
        errors = []

        # This is dumb.  filters is a django QueryDict, but QueryDicts do not
        # return the same thing when filters.items() is invoked.  Depending on
        # the phase of the moon, they will return either the item, or the item
        # wrapped in a list.
        for k in filters.keys():
            v = filters.getlist(k)
            try:
                # Populate self.filters and do validation on fields and values
                self.parse(k, v)
            except FilterError as e:
                # Some sort of error occured, populate our error list
                errors.append(e)

        # If we have any filtering errors, just throw them.
        if errors:
            raise exceptions.BadRequest({e.name: e.message for e in errors})

        # Get a Q object and filter
        q = self.q()
        return iterable.filter(q)
