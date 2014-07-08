
class Resource:

    def __init__(self, slug=None, context=None):
        """
        :param slug: Identifier that represents which item of the resource
                     to return, if present.
        :type context: str or None

        :param context: Context in which this resource is being called (eg.
                        a nested resource will receive the result of a `read`
                        from the parent resource in its context).
        :type context: dict or None
        """
        self.slug = slug
        self.context = context or {}
