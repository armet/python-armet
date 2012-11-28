# -*- coding: utf-8 -*-
"""Implements the RESTful resource protocol for django ORM-backed models.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from . import base
import six


class BaseModel(base.BaseResource):

    #! The model this resource is bound to; shortcut for declaring a form
    #! for read-only resources.
    model = None

    #! Class object cache of what is to be prefetched.
    _prefetch_related_paths = []

    def prefetch_related(self, queryset):
        """Performs a `prefetch_related` on all possible fields."""
        if not self._prefetch_related_paths and len(queryset) >= 1:
            # Get sorted list of path elements
            field_paths = [x.path for x in six.itervalues(self._fields)]
            field_paths.sort(reverse=True)

            # Cache of what to prefetch has not been built; build it.
            for field_path in field_paths:
                segments = field_path.split('__')
                for index in range(len(segments), 0, -1):
                    try:
                        # Attempt to prefetch
                        path = '__'.join(segments[:index])
                        queryset.prefetch_related(path)[0]

                    except (ValueError, AttributeError):
                        # Not able to prefetch; move along
                        pass

                    else:
                        # Worked somehow; store it and get out
                        self._prefetch_related_paths.append(path)
                        break

            # Ensure cache is unique and sorted properly
            self._prefetch_related_paths = sorted(
                set(self._prefetch_related_paths), reverse=True)

        # Actually apply the prefetched prefetching
        return queryset.prefetch_related(*self._prefetch_related_paths)

    @classmethod
    def slug(cls, obj):
        return obj.pk

    def read(self):
        return self.prefetch_related(self.model.objects.all())
