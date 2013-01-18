# -*- coding: utf-8 -*-
"""Implements the RESTful resource protocol for django ORM-backed models.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from . import base
from .. import exceptions, authorization, utils


class BaseModel(base.BaseResource):

    #! The model this resource is bound to; shortcut for declaring a form
    #! for read-only resources.
    model = None

    #! Declares a resource to be the primary provider of the associated model.
    #! There cannot be two resources linked to the same model with
    #! `canonical = True`.
    canonical = True

    #! Whether to use prefetch_related or not to reduce the number of
    #! database queries.
    # TODO: If this is disabled `.iterator` should be used to access the
    #   queryset.
    prefetch = True

    @utils.classproperty
    def _prefetch_related_cache(cls):
        if cls._prefetchable and cls.model.objects.all().exists():
            # Initialize the cache and declare us as no longer prefetchable
            cls._prefetchable = False
            cls._prefetch_cache = set()

            # Cache has not yet been made; we should do this.
            for attribute in six.itervalues(cls._attributes):
                if not attribute.visible or not attribute.path:
                    # Attribute is not visible or has no path.
                    continue

                if attribute.relation is not None:
                    # This is a related attribute; attempt to explode the
                    # prefetchable attributes of the related resource.
                    rel = attribute.relation.resource._prefetch_related_cache
                    if rel:
                        # We have some sort of cache listing from the related
                        # resource.
                        path = '__'.join(attribute.path)
                        join = lambda x: '{}__{}'.format(path, x)
                        cls._prefetch_cache.update(map(join, rel))

                        # The cache of a related resource implies the
                        # cache of this attribute; skip it.
                        continue

                # Enumerate through a path so we attempt sub sections in order.
                # Eg. for apple__fruit__orange we try that first than
                # apple__fruit and so on.
                for index in reversed(range(len(attribute.path))):
                    path = '__'.join(attribute.path[index:])
                    try:
                        # Attempt to prefetch by the constructed path
                        cls.model.objects.all().prefetch_related(path)[0]

                    except (ValueError, AttributeError):
                        # Prefetch failed; move along.
                        continue

                    # Prefetch was successful; append this path to our cache
                    # and break out of this loop.
                    cls._prefetch_cache.add(path)
                    break

        # The cache exists; return it and hope it doesn't break.
        return cls._prefetch_cache

    @classmethod
    def make_slug(cls, obj):
        # TODO: This method should be declarative instead of functional to
        #   faciliate interacting with the slug elsewhere.
        return str(obj.pk)

    def read(self):
        # Initially instantiate a queryset representing every object.
        queryset = self.model.objects.all()

        # Filter the queryset based on several possible factors.
        # The query is just a Q object which django natively consumes.
        queryset = queryset.filter(self.query.as_q())

        if self.slug is not None:
            # Filter the queryset based on the current slug.
            # TODO: Allow configuring what property the slug corresponds to.
            queryset = queryset.filter(pk=self.slug)

        if self.prefetch:
            # Prefetch all related attributes and store in a cache.
            # This significantly reduces the number of queries.
            queryset = queryset.prefetch_related(*self._prefetch_related_cache)

        # Return the queryset if we still have it.
        return queryset

    def destroy(self, queryset):
        # The object should be a queryset or a model; delete the model(s).
        queryset.delete()
