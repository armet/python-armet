""" A file for filtering
"""

from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.utils.functional import cached_property
from . import exceptions


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
                #     raise exceptions.BadRequest(
                #         'Filtering is not allowed on {}'.format(filtermap[0]))

                # Navigate to a relation
                if idx < len(filtermap):
                    if field.relation is None:
                        # This is not a relational field
                        raise exceptions.BadRequest(
                            '{} is not a related field'.format(field_string))
                    fields = field.relation._fields

        except KeyError as e:
            # Happens when field_string can't be found in the fields lookup
            raise exceptions.BadRequest(
                '{} is not a valid field'.filter(e.message))

    def parse(self, filter):
        """Parses filters and checks to see if our filter params are valid.
        Filters that do not appear in the fields list are not valid.  Returns
        a string
        """
        # Slice up the parameter into its components
        items = filter.split('__')

        # Check to see if our filter ends with a 'neq' and slice it off the
        # search query
        if items[-1] == 'not':
            items = items[:-1]
            invert = True
        else:
            invert = False

        # Grab the last item and see if its a valid terminator.  Remove valid
        # terminators for the purposes of item lookup
        terminator = items[-1]
        if terminator in self.terminators:
            items = items[:-1]
        else:
            terminator = None

        # Make sure that we're allowed to filter this
        self.can_filter(items)

        # Tack on the terminator again
        if terminator is not None:
            items.append(terminator)

        # We're all good, return the query string, and the invert boolean
        return LOOKUP_SEP.join(items), invert


class Model(Filter):
    """model specific filtering stuff
    """

    def filter(self, iterable, filters):
        query = Q()
        for k, value in filters.items():
            qstring, inverted = self.parse(k)
            # Values may be lists of things, in which case they must be "or"ed
            if not isinstance(value, basestring):
                # Not a string, try iterating over it
                try:
                    q = [Q(**{qstring:x}) for x in value]
                    query &= reduce(lambda x, y: x | y, q)
                    # It was an iterable, continue to the next item
                    continue
                except TypeError:
                    # This isn't iterable, its probably an int or something
                    pass
            # Its not a list, proceed as usual doing the and stuff
            print qstring, value
            q = Q(**{qstring: value})
            if inverted:
                q = ~q
            query &= q

        return iterable.filter(query)
