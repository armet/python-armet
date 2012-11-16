import six
from . import base, meta


class Resource(six.with_metaclass(meta.Resource, base.Resource)):
    pass


# from .model import Resource as Model


__all__ = [
    Resource
]
