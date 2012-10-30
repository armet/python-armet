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
    def resolve(cls, path, full=False, **kwargs):
        # Delegate to the base resource to do the actual resolution
        resolution = super(Model, cls).resolve(path, **kwargs)

        if not full:
            try:
                # Attempt to grab the slug from the resolution as an object;
                # The normal path (ChoiceField) expects the entire resolved
                # resource but (ModelChoiceField) expects only the pk
                return resolution[cls.model._meta.pk.name]

            except:
                # Wasn't a model apparently; just return the resolution
                pass

        # Pass us on
        return resolution

    @property
    def queryset(self):
        """Queryset that is used to read and filter data."""
        if self.params is not None:
            # Parameter-based filtering (for foreign key navigation).
            return self.model.objects.filter(**self.params)

        else:
            # No parameters; just return them all
            return self.model.objects.all()

    def exists(self):
        """Implementation of `exists` using django models."""
        return self.queryset.filter(**{self.slug: self.identifier}).exists()

    def read(self):
        """Implementation of `read` using django models."""
        if self.identifier is not None:
            try:
                # This is an individual resource; attempt to get it
                return self.queryset.get(**{self.slug: self.identifier})

            except:
                # Well damn; we don't have one -- die
                raise exceptions.NotFound()

        else:
            # Just get them all; hehehe..
            return self.queryset

    def create(self, obj):
        # Iterate through and set all fields that we can initially
        params = {}
        for name, field in self._fields.iteritems():
            if name not in obj:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection:
                # This is a m2m field; move along for now
                continue

            # This is not a m2m field; we can set this now
            params[name] = obj[name]

        # Perform the initial create
        model = self.model.objects.create(**params)

        # Iterate through again and set the m2m bits
        for name, field in self._fields.iteritems():
            if name not in obj or not obj[name]:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection:
                # This is a m2m field; we can set this now
                setattr(model, field.name, obj[name])

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

    def update(self, old, obj):
        # `old` comes from `read` which is in my control and I return a model
        # Iterate through the fields and set or destroy them
        for name, field in self._fields.iteritems():
            if field.direct:
                value = obj[name] if name in obj else None
                setattr(old, name, value)

        # Save and we're off
        old.save()

        # Return the new model
        return old

    def destroy(self):
        # Delegate to django to perform the creation
        self.model.objects.get(**{self.slug: self.identifier}).delete()
