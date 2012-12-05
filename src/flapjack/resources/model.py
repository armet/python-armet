# -*- coding: utf-8 -*-
"""Implements the RESTful resource protocol for django ORM-backed models.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from . import base
from .. import exceptions


class BaseModel(base.BaseResource):

    #! The model this resource is bound to; shortcut for declaring a form
    #! for read-only resources.
    model = None

    #! Class object cache of what is to be prefetched.
    _prefetch_related_paths = {}

    @classmethod
    def _build_prefetch_related_paths(cls, queryset, prefix=None, skip=None):
        # Initialize the store
        prefetched = []

        # Get sorted list of visibile path elements
        field_paths = []
        for field in six.itervalues(cls._fields):
            if field.visible:
                field_paths.append(field.path)

        field_paths.sort(reverse=True)

        # Cache of what to prefetch has not been built; build it.
        # First iterate and store all field names
        for field_path in field_paths:
            if field_path is None:
                # No field path; nothing to check.
                continue

            for index in range(len(field_path), 0, -1):
                try:
                    # Attempt to prefetch
                    path = '__'.join(field_path[:index])
                    if prefix:
                        path = '{}__{}'.format(prefix, path)

                    queryset.prefetch_related(path)[0]

                except (ValueError, AttributeError):
                    # Not able to prefetch; move along
                    pass

                else:
                    # Worked somehow; store it and get out
                    prefetched.append(path)
                    break

        if skip is None:
            # Initialize skip list if we need to.
            skip = []

        for name, field in six.iteritems(cls._fields):
            relation = field.relation
            if relation and issubclass(relation.resource, BaseModel):
                # Do we need to skip this?
                if relation in skip:
                    continue

                # Nope; add to skip list
                skip.append(relation)

                # Attempt to apply a test prefetch related
                paths = relation.resource._build_prefetch_related_paths(
                    queryset, prefix=field.path, skip=skip)

                # Append these to our list as well
                prefetched.extend(paths)

        # Ensure cache is unique and sorted properly
        return sorted(set(prefetched), reverse=True)

    @classmethod
    def prefetch_related(cls, queryset, prefix=None):
        """Performs a `prefetch_related` on all possible fields."""
        if id(cls) not in cls._prefetch_related_paths and len(queryset) >= 1:
            # Initialize the store
            cls._prefetch_related_paths[id(cls)] = cls._build_prefetch_related_paths(
                queryset, prefix)

        if id(cls) in cls._prefetch_related_paths:
            # Actually apply the prefetched prefetching
            return queryset.prefetch_related(
                *cls._prefetch_related_paths[id(cls)])

        # Apply nothing.
        return queryset

    @classmethod
    def make_slug(cls, obj):
        return str(obj.pk)

    def read(self):
        # Build the queryset
        queryset = self.model.objects

        try:
            # Apply transveral first.
            # Build filter string for parents
            parent = self.parent
            path = []
            while parent is not None:
                path.append(parent.related_name)
                queryset = queryset.filter(**{'__'.join(path): parent.slug})
                parent = parent.resource.parent

            if self.slug is not None:
                # Model resources by default have the slug as the identifier.
                # TODO: Support non-pk slugs easier by allowing a
                #   hook or something.
                queryset = queryset.filter(pk=self.slug)

        except ValueError:
            # Something went wront when applying the slug filtering.
            raise exceptions.NotFound()

        else:
            # No slug; start with all the models.
            queryset = queryset.all()

        # Prefetch all related fields and return the queryset.
        return self.prefetch_related(queryset)
