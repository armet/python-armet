import six
from . import meta
from .base import BaseResource
from .model import BaseModel


class Resource(six.with_metaclass(meta.Resource, BaseResource)):
    """Implements the RESTful resource protoocl for generic resources.

    Derive from this class to extend and create your own generic resources.

    @example
        from flapjack import resources


        class MyResource(resources.Resource):

            def read(self):
                return {'question': None, 'answer': 42}
    """
    pass


class Model(six.with_metaclass(meta.Model, BaseModel)):
    pass


__all__ = [
    BaseResource,
    Resource,
    BaseModel,
    Model
]
