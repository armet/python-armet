# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.utils import compose
from collections import defaultdict
from functools import partial


class Attribute(object):
    """Generic attribute.

    Use this to indicate that the type of the data is unmanaged by armet.
    This is also an extension point for further attributes.
    """

    #! Python type expected to be marshalled through this attribute.
    type = None

    def __init__(self, path=None, **kwargs):

        #! Attribute may be accessed directly.
        #! Note that setting this to false will still show the attribute in
        #! the body. Set include to false to hide it from the body.
        self.read = kwargs.get('read', True)

        #! Attribute may be modified through any operation.
        self.write = kwargs.get('write', True)

        #! Attribute is included in the response body.
        self.include = kwargs.get('include', True)

        #! Attribute can accept a null value.
        self.null = kwargs.get('null', True)

        #! Attribute must be present in the body.
        self.required = kwargs.get('required', False)

        #! Attribute is to be treated as a collection.
        self.collection = kwargs.get('collection', False)

        #! Override python name of the attribute.
        self.name = kwargs.get('name')

        #! Flag to turn the set operation into a no-op.
        # HACK: This is in-place in order to get around a bug I've encountered
        #   until relationships are implemented.
        self._set = kwargs.get('_set', True)

        #! The path reference of where to find this attribute on an
        #! item (eg. 'name' references the name key if the read method returns
        #! a dictionary.)
        #!
        #! The path may be dot-separated to indicate simple traversal.
        #! Eg. user.name could be obj['user'].name
        self.path = path
        if self.path:
            # Explode the path into segments to iterate over in operations.
            self._segments = defaultdict(lambda: self.path.split('.'))

        # Attributes use a lazy optimization process for attribute lookup
        # on the underlying data model. When an attribute is accessed
        # it builds and caches the operation action.
        self._getters = defaultdict(list)

        # Attribute cache that is keyed on the type of the target object.
        this = self

        class GetResolver(dict):

            def __missing__(self, key):
                return partial(this._resolve_get, self, key.__class__)

        self._get = GetResolver()

    def _resolve_get(self, resolver, key, target):
        if self.path is None:
            # There is no path defined on this resource.
            # We can do no magic to get the value.
            resolver[key] = lambda *a: None
            return None

        # Iterate and resolve each constructed getter.
        for func in self._getters[key]:
            if target is None:
                # No more getters can be resolved.
                return None

            # Resolve this getter and continue iteration.
            target = func(target)

        # Are their segments remaining to make a getter for?
        while self._segments[key]:
            if target is None:
                # No more getters can be made.
                return None

            # Fetch the next path segment.
            segment = self._segments[key].pop(0)

            # Make and append the corresponding getter.
            func = self._make_getter(segment, key)
            self._getters[key].append(func)

            # Resolve the getter.
            target = func(target)

        # Have we finished resolving the getters?
        if not self._segments[key]:
            # Compose a replacement get function that just iterates over
            # the getters.
            resolver[key] = compose(*self._getters[key])

        # Return our resolved value.
        return target

    def get(self, target):
        """Retrieve the value of this attribute from the passed object.
        """

        # Attempt to resolve an accessor for the specific target. Creates
        # the accessor if not available.
        return self._get[target](target)

    def set(self, target, value):
        """Set the value of this attribute for the passed object.
        """

        if not self._set:
            return

        if self.path is None:
            # There is no path defined on this resource.
            # We can do no magic to set the value.
            self.set = lambda *a: None
            return None

        if self._segments[target.__class__]:
            # Attempt to resolve access to this attribute.
            self.get(target)

        if self._segments[target.__class__]:
            # Attribute is not fully resolved; an interim segment is null.
            return

        # Resolve access to the parent object.
        # For a single-segment path this will effectively be a no-op.
        parent_getter = compose(*self._getters[target.__class__][:-1])
        target = parent_getter(target)

        # Make the setter.
        func = self._make_setter(self.path.split('.')[-1], target.__class__)

        # Apply the setter now.
        func(target, value)

        # Replace this function with the constructed setter.
        def setter(target, value):
            func(parent_getter(target), value)

        self.set = setter

    def prepare(self, value):
        """Prepare the value for serialization and presentation to the client.
        """

        # By default, do nothing to the value.
        return value

    def clean(self, value):
        """Cleans the value from deserialization into consumption by python.
        """

        # By default, do nothing to the value.
        return value

    def try_clean(self, value):
        try:
            # TODO: Remove usage of this in query builder.
            return self.clean(value)

        except (ValueError, AssertionError):
            return None

    def clone(self):
        """Construct an identical attribute.

        Used by the resource metaclass to ensure all attributes are unique
        instances. This is done so that when getters and setters are resolved
        the caches don't clobber base classes (for inherited attributes).
        """

        return self.__class__(**self.__dict__)

    def _make_getter(self, segment, class_):

        # Attempt to resolve properties and simple functions by
        # accessing the class attribute directly.
        obj = getattr(class_, segment, None)
        if obj is not None:
            if hasattr(obj, '__call__'):
                return obj.__call__

            if hasattr(obj, '__get__'):
                return lambda target, x=obj.__get__: x(target, class_)

        # Check for much better hidden descriptor.
        obj = class_.__dict__.get(segment)
        if obj is not None and hasattr(obj, '__get__'):
            return lambda target, x=obj.__get__: x(target, class_)

        # Check for item access (for a dictionary).
        if hasattr(class_, '__getitem__'):
            def getter(target):
                try:
                    return target[segment]

                except KeyError:
                    return None

            return getter

        # Check for attribute access.
        if hasattr(class_, '__dict__'):
            return lambda target: target.__dict__.get(segment)

        raise RuntimeError(
            'unable to resolve attribute access for %r on %r' % (
                segment, class_))

    def _make_setter(self, segment, class_):

        # Attempt to resolve a data descriptor.
        obj = getattr(class_, segment, None)
        if obj is not None:
            if hasattr(obj, '__set__'):
                def setter(target, value, x=obj.__set__):
                    x(target, value)

                return setter

        # Check for much better hidden descriptor.
        obj = class_.__dict__.get(segment)
        if obj is not None and hasattr(obj, '__set__'):
            def setter(target, value, x=obj.__set__):
                x(target, value)

            return setter

        # Check for item access (for a dictionary).
        if hasattr(class_, '__getitem__'):
            def setter(target, value):
                target[segment] = value

            return setter

        # Check for attribute access.
        if hasattr(class_, '__dict__'):
            def setter(target, value):
                target.__dict__[segment] = value

            return setter

        raise RuntimeError(
            'unable to resolve attribute setter for %r on %r' % (
                segment, class_))
