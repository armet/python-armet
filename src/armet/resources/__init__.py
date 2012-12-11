import six
from .meta import DeclarativeResource, DeclarativeModel
from .base import BaseResource
from .model import BaseModel
from .helpers import field, relation
import logging

logging.basicConfig()


class Resource(six.with_metaclass(DeclarativeResource, BaseResource)):
    """Implements the RESTful resource protoocl for generic resources.

    Derive from this class to extend and create your own generic resources.

    @example
        from armet import resources


        class MyResource(resources.Resource):

            def read(self):
                return {'question': None, 'answer': 42}
    """
    pass


class Model(six.with_metaclass(DeclarativeModel, BaseModel)):
    """Implements the RESTful resource protoocl for model-bound resources.

    Derive from this class to extend and create your own model-bound resources.

    @example
        from armet import resources
        from . import models


        class MyResource(resources.ModelResource):

            def read(self):
                return {'question': None, 'answer': 42}
    """


__all__ = [
    BaseResource,
    Resource,
    BaseModel,
    Model,
    field,
    relation
]
