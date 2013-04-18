# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.http import response
from six.moves import cStringIO as StringIO


class Headers(response.Headers):

    def __init__(self, handler):
        self.__handler = handler
        super(Response, self).__init__()

    def __setitem__(self, name, value):
        self.handler.set_header(name, value)

    def __getitem__(self, name):
        # Cyclone doesn't provide a way to get headers normally, so break
        # into the private methods to retrieve the header.
        return self.handler._headers[name]

    def __contains__(self, name):
        return name in self.handler._headers

    def __delitem__(self, name):
        self.handler.clear_header(name)

    def __len__(self):
        return len(self.handler._headers)

    def __iter__(self):
        return iter(self.handler._headers)
# # -*- coding: utf-8 -*-
# from __future__ import absolute_import, unicode_literals, division

class Response(response.Response):
    pass

#     def __init__(self, handler, *args, **kwargs):
#         super(Response, self).__init__(*args, **kwargs)
#         self.handler = handler

#     def __setitem__(self, name, value):
#         self.handler.set_header(name, value)

#     def __getitem__(self, name):
#         # Cyclone doesn't provide a way to get headers normally, so break
#         # into the private methods to retrieve the header.
#         return self.handler._headers[name]

#     def __contains__(self, name):
#         return name in self.handler._headers

#     def __delitem__(self, name):
#         self.handler.clear_header(name)

#     def __len__(self):
#         return len(self.handler._headers)

#     def __iter__(self):
#         return iter(self.handler._headers)

#     @property
#     def status(self):
#         return self.handler.get_status()

#     @status.setter
#     def status(self, value):
#         self.handler.set_status(value)

#     def write(self, chunk):
#         self.handler.write(chunk)
