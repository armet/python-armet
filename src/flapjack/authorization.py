"""Contains authorization stuff
"""


class Authorization(object):
    """docstring for Authorization"""
    def __init__(self, request, method):
        super(Authorization, self).__init__()
        self.request = request
        self.method = method

    @property
    def is_accessible(self):
        """Immediate authorization (eg, only admins may access a resource)
        """
        return True

    @property
    def is_authorized(self, obj):
        """Authorization pass after the object has been constructed
        """
        return True

    def limit_queries(self, query):
        """Apply query limits to the result list
        """
        return query
