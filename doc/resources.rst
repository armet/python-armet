Resources
*********

Options
=======
The following configurable properties are available to be set as attributes
directly on a resource for per-resource configuration.

``http_method_names``
---------------------
The full list of understood -- but not neccessarily supported -- HTTP methods.

Unless otherwise specified, the default values are as follows: ::

    http_method_names = (
            'options',  # RFC 2616 § 9.2
            'get',      #          § 9.3
            'head',     #          § 9.4
            'post',     #          § 9.5
            'put',      #          § 9.6
            'delete',   #          § 9.7
            'trace',    #          § 9.8
            'connect',  #          § 9.9
            'patch',    # RFC 5789 [PROPOSED STANDARD]
        )

.. note::
    This *should* at least be a superset of http_allowed_methods_.

``http_allowed_methods``
------------------------
