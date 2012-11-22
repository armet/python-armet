Resources
*********

Options
=======
The following configurable properties are available to be set as attributes
directly on a resource for per-resource configuration.

``http_method_names``
---------------------
The full list of understood, but not neccessarily supported, HTTP methods (
in lowercase).

According to `RFC 2616 § 10.5.2`_ a server should return a ``501`` response if
it is incapable of understanding the request method.

.. _RFC 2616 § 10.5.2: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.5.2

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
        'patch',    # RFC 5789
    )

.. note::
    This *should* at least be a superset of http_allowed_methods_ as the method
    of the incoming ``HTTPRequest`` is matched against this list before the
    list of allowed methods.

``http_allowed_methods``
------------------------
The list of allowed HTTP methods.

Unless otherwise specified, the default values are as follows: ::

    http_allowed_methods = (
        'get',
        'post',
        'put',
        'delete',
    )
