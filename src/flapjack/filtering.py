""" A file for filtering
"""

from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.utils.functional import cached_property
from . import exceptions


class Filter(object):
    """docstring for Model"""
    def __init__(self, fields, allowed):
        self.fields = fields
        self.allowed = allowed

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
        if filtermap[0] not in self.allowed:
            raise exceptions.BadRequest(
                '{} is not filterable'.format(filtermap[0]))
        # TODO: navigate to other resources

    def parse(self, filter):
        """Parses filters and checks to see if our filter params are valid.
        Filters that do not appear in the fields list are not valid.
        """
        # Slice up the parameter into its components
        items = filter.split('__')

        # Check to see if our filter ends with a 'neq' and slice it off the
        # search query
        if items[-1] is 'neq':
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

    def filter(self, iterable, filters):
        query = Q()
        for x in filters:
            qstring, inverted = self.parse(x)
            if inverted:
                q = not Q(qstring)
            else:
                q = Q(qstring)
            query &= q

        return iterable.filter(query)
