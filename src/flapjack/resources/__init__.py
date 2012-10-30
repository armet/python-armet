import six
from .meta import Resource
from .base import Base
from .model import *


class Resource(six.with_metaclass(Resource, Base)):
    pass


__all__ = [
    Resource,
    Model
]
