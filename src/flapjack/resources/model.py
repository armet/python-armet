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
    _prefetch_related_paths = None

    @classmethod
    def prefetch_related(cls, queryset, prefix=None):
        """Performs a `prefetch_related` on all possible fields."""
        if not cls._prefetch_related_paths and len(queryset) >= 1:
            # Get sorted list of path elements
            field_paths = [x.path for x in six.itervalues(cls._fields)]
            field_paths.sort(reverse=True)

            # Cache of what to prefetch has not been built; build it.
            # First iterate and store all field names
            for field_path in field_paths:
                segments = field_path.split('__')
                for index in range(len(segments), 0, -1):
                    try:
                        # Attempt to prefetch
                        path = '__'.join(segments[:index])
                        if prefix:
                            path = '{}__{}'.format(prefix, path)

                        queryset.prefetch_related(path)[0]

                    except (ValueError, AttributeError):
                        # Not able to prefetch; move along
                        pass

                    else:
                        # Worked somehow; store it and get out
                        cls._prefetch_related_paths.append(path)
                        break

            for name, field in six.iteritems(cls._fields):
                if field.relation and issubclass(field.relation[0], BaseModel):
                    # Attempt to apply a test prefetch related
                    field.relation[0].prefetch_related(queryset,
                        prefix=field.path)

                    # Append these to our list as well
                    cls._prefetch_related_paths.extend(
                        field.relation[0]._prefetch_related_paths)

            # Ensure cache is unique and sorted properly
            cls._prefetch_related_paths = sorted(
                set(cls._prefetch_related_paths), reverse=True)

        # Actually apply the prefetched prefetching
        return queryset.prefetch_related(*cls._prefetch_related_paths)

    @classmethod
    def slug(cls, obj):
        return obj.pk

    def read(self):
        return self.prefetch_related(self.model.objects.all())
