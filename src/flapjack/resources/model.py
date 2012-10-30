import six
from .. import filtering, exceptions
from . import meta, base


class Model(six.with_metaclass(meta.Model, base.Base)):
    """Implementation of a `RESTful` resource using django models.
    """

    #! Model class object to use to bind to this resource.
    #! Is overridden by the model option in the ModelForm form if specified.
    model = None

    #! Class object of the filter class to proxy filtering to for filtering
    #! filterables, specialized for model resources.
    filterer = filtering.Model

    @classmethod
    def resolve(cls, path, request, full=False, **kwargs):
        # Delegate to the base resource to do the actual resolution
        resolution = super(Model, cls).resolve(path, request, **kwargs)

        if not full:
            try:
                # Attempt to grab the slug from the resolution as an object;
                # The normal path (ChoiceField) expects the entire resolved
                # resource but (ModelChoiceField) expects only the pk
                return getattr(resolution, cls.model._meta.pk.name)

            except:
                # Wasn't a model apparently; just return the resolution
                pass

        # Pass us on
        return resolution

    # def form_clean(self, obj):
    #     if self.identifier is not None:
    #         # Get the model instance; this allows the form to validate even
    #         # without the presence of `required` model fields.
    #         return self.form(data=obj, instance=self.queryset[0])

    #     return super(Model, self).form_clean(obj)

    @property
    def queryset(self):
        """Queryset that is used to read and filter data."""
        # Start with them all
        queryset = self.model.objects.all()

        if self.params is not None:
            # Parameter-based filtering (for foreign key navigation).
            queryset = queryset.filter(**self.params)

        # Return the constructed queryset
        return queryset

    def read(self):
        """Implementation of `read` using django models."""
        if self.identifier is not None:
            # This is an individual resource; attempt to get it
            return self.queryset.filter(**{self.slug: self.identifier})

        else:
            # Just get them all; hehehe..
            return self.queryset

    def create(self, data):
        # Iterate through and set all fields that we can initially
        params = {}
        for name, field in self._fields.iteritems():
            if name not in data:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection:
                # This is a m2m field; move along for now
                continue

            if not field.editable:
                # Field is not editable; move along.
                continue

            # This is not a m2m field; we can set this now
            params[name] = data[name]

        # Perform the initial create
        model = self.model.objects.create(**params)

        # Iterate through again and set the m2m bits
        for name, field in self._fields.iteritems():
            if name not in data or not data[name]:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection \
                    and field.editable:
                # This is a m2m field; we can set this now
                setattr(model, field.name, data[name])

        # Iterate through and set all direct parameters
        for param in self.params:
            field = self._fields.get(param)
            if field is not None and field.direct:
                setattr(model, field.name, param)

        # Perform a final save
        model.save()

        # Iterate through and set all "in"direct parameters
        for param, value in self.params.items():
            field = self._fields.get(param)
            if field is not None and not field.direct:
                if field.collection:
                    getattr(model, field.related_name).add(value)
                    model.save()

        # Return the fully constructed model
        return model

    def update(self, obj, data):
        # `obj` comes from `read` which is in my control and I return a model
        # Iterate through the fields and set or destroy them
        for name, field in self._fields.iteritems():
            print(name, field, field.editable)
            if field.editable:
                value = data[name] if name in data else None
                setattr(obj, name, value)

        # Save and we're off
        obj.save()

        # Return the new model
        return obj

    def destroy(self, obj):
        # Delegate to django to perform the creation
        obj.delete()
