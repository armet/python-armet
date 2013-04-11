# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
import mock
import contextlib
import importlib
import functools


class Wrapper:

    def __init__(self, mock):
        self.mock = mock

    def __call__(self, function):
        def wrapped(obj, *args, **kwargs):
            self.mock(*args, **kwargs)
            return function(obj, *args, **kwargs)

        return wrapped


@contextlib.contextmanager
def spy(target, method):
    # Retrieve a reference to the class object.
    segments = target.split('.')
    module = '.'.join(segments[:-1])
    module = importlib.import_module(module)
    target = getattr(module, segments[-1])

    # Create the mock.
    save = getattr(target, method)
    mocked = mock.MagicMock()
    wrapped = Wrapper(mocked)(save)
    setattr(target, method, wrapped)

    try:
        # Yield to the block.
        yield mocked

    except AttributeError:
        # Something weird happened because of our spy; oh well.
        pass

    # Restore the method.
    setattr(target, method, save)
