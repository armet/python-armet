"""Contains authentication stuff
"""


class Authentication(object):
    """docstring for Authentication"""
    def __init__(self, request):
        super(Authentication, self).__init__()
        self.request = request

    @property
    def is_authenticated(self):
        return True
