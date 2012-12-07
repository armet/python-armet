""" ..
"""
import datetime
import six
import pickle
import magic
from .http import HttpResponse
from . import exceptions, transcoders, utils
from collections import Iterable, OrderedDict

class Bin(transcoders.Bin, Encoder):

    @classmethod
    def encode(cls, obj=None,in_browser=False):
        try:
            # transmit a binary file from the server
            bindata = obj.read()
            response = super(Bin, cls).encode(bindata)
            if in_browser == False:
                response['Content-Disposition'] = \
                    'attachment; filename="{}"'.format(obj.name.split('/')[-1])
#            response['Content-Type'] = str(mimetypes.types_map[ re.search('\.[^.]*$',obj.name).group(0)])
            response['Content-Type'] = magic.from_buffer(bindata, mime=True)
        except AttributeError:
            # pickle a python object
            response = super(Bin, cls).encode(pickle.dumps(obj,protocol=2))
            response['Content-Disposition'] = \
            'attachment'
        return response

            

# I know this is the hackiest possible way to do it.
# TODO: clean up this code

@Encoder.register()
class Bin(transcoders.Bin, Encoder):

    @classmethod
    def encode(cls, obj=None,in_browser=False):
        try:
            # transmit a binary file from the server
            bindata = obj.read()
            response = super(Bin, cls).encode(bindata)
            if in_browser == False:
                response['Content-Disposition'] = \
                    'attachment; filename="{}"'.format(obj.name.split('/')[-1])
#            response['Content-Type'] = str(mimetypes.types_map[ re.search('\.[^.]*$',obj.name).group(0)])
            response['Content-Type'] = magic.from_buffer(bindata, mime=True)
        except AttributeError:
            # pickle a python object
            response = super(Bin, cls).encode(pickle.dumps(obj,protocol=2))
            response['Content-Disposition'] = \
            'attachment'
        return response

