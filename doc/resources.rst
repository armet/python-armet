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

``http_list_allowed_methods``
-----------------------------
The list of allowed HTTP methods that can be performed on
a whole resource (eg /user).
If undeclared or None, will be defaulted to `http_allowed_methods`.

Unless otherwise specified, the default value is: ``None``

``http_detail_allowed_methods``
-------------------------------
The list of allowed HTTP methods that can be performed against
a single resource (eg /user/1).
If undeclared or None, will be defaulted to `http_allowed_methods`.

Unless otherwise specified, the default values are as follows: ``None``

``allowed_operations``
----------------------
Resource operations are meant to generalize and blur the
differences between "PATCH and PUT", "PUT = create / update", etc.

Unless otherwise specified, the default values are as follows: ::

    allowed_operations = (
        'read',
        'create',
        'update',
        'destroy',
    )

``list_allowed_operations``
---------------------------
List of allowed operations against a whole resource.
If undeclared or None, will be defaulted to `allowed_operations`.

Unless otherwise specified, the default values are as follows: ``None``

``detail_allowed_operations``
-----------------------------
List of allowed operations against a single resource.
If undeclared or None, will be defaulted to `allowed_operations`.

Unless otherwise specified, the default values are as follows: ``None``

``allowed_encoders``
--------------------
List of allowed encoders.

Unless otherwise specified, the default values are as follows: ::

    allowed_encoders = (
        'json',
    )

``default_encoder``
-------------------
Name of the default encoder of the list of understood encoders.

Unless otherwise specified, the default values are as follows: ::

    default_encoder = 'json'

``decoders``
------------
List of decoders known by this resource.

Unless otherwise specified, the default values are as follows: ::

    decoders = (
        'flapjack.decoders.Form',
    )

``url_name``
------------
URL namespace to define the url configuration inside.

Unless otherwise specified, the default values are as follows: ::

    url_name = 'api_view'

``exlude``
----------
Blacklist of fields to exclude from display.

Unless otherwise specified, the default values are as follows: ::

    exclude = None

``fields``
----------
Whitelist of fields to include in the display.

Unless otherwise specified, the default values are as follows: ::

    fields = None

``include``
-----------
Additional fields to include in the display.

Unless otherwise specified, the default values are as follows: ::

    include = None

``filterable``
--------------
Whitelist of fields that are filterable.
Default is to be an empty () which excludes all fields from filtering.
To have all fields be eligible for filtering, explicitly specify
`filterable = None` on a resource or any of its parents.

Unless otherwise specified, the default values are as follows: ::

    filterable = None

``resource_uri``
----------------
The name of the resource URI field on the resource.
Specify `None` to not have the URI be included.

Unless otherwise specified, the default values are as follows: ::

    resource_uri = 'resource_uri'

``authentication``
------------------
 Authentication protocol(s) to use to authenticate access to the resource.

Unless otherwise specified, the default values are as follows: ::

    authentication = ('flapjack.authentication.Authentication',)

``relations``
-------------
Dictionary of the relations for this resource; maps the names of the
fields to the resources they relate to. The key is the name of the
field on the resource; the value is a call to the `resources.relation`
method found in resources.helpers (and imported into resources).

Unless otherwise specified, the default values are as follows: ::

    relations = None

``make_slug``
-------------
The resource URI segment which is used to access and identify this resource.

Example::

    @classmethod
    def make_slug(cls, obj):
        return str(obj.pk)

.. note::
    This method is only valid and used if this resource is exposed via an urls.py.
