# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from __future__ import absolute_import
import contextlib
import importlib
import sys
import functools
import six


if sys.version_info[0] == 2 or sys.version_info[1] < 3:
    # Mock is only provided in >= python 3.3
    import mock

else:
    from unittest import mock


class Wrapper:

    def __init__(self, mock):
        self.mock = mock

    def __call__(self, function):
        def wrapped(obj, *args, **kwargs):
            self.mock(*args, **kwargs)
            result = function(*args, **kwargs)
            self.mock.return_value = result
            return result

        return functools.partial(wrapped, six.get_method_self(function))


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

    # Yield to the block.
    yield mocked

    # Restore the method.
    setattr(target, method, save)
