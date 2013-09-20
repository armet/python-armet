## 0.4.0 (unreleased)

 - Catch assertions and value errors during the attribute cleaning cycle and send the messages back as a serialized 400 response to the client.

 - Removed deprecated `include` resource option for declaring attributes.

 - Changed `slug` resource option to a string that maps to an existing attribute by their name.

 - Moved attributes out of `armet.resources`. `armet.resources.*Attribute` becomes `armet.attributes.*Attribute`.

 - Facilitate properties defined for attributes:
    - `read` (default `True`) — attribute may be accessed directly (eg. `GET /resource/attribute` or `GET /resource/1/attribute`). Note that setting this to `False` will still show the attribute in the body of `GET /resource`. Set `include` to `False` to hide it from the body.

    - `write` (default `True`) ­— attribute may be modified through any operation (`POST`, `PUT`, or `PATCH` on the body or directly). This can be set to `True`, `False`

    - `include` (default `True`) — attribute is included in the response body. This can be set to `True`, `False`

    - `null` (default: `True`) — attribute can accept a `null` value. This is only checked (for obvious reasons) at modification operations and results in a validation error. This can be set to `True`, `False`

    - `required` (default: `False`) — attribute must be present in the body. This is only checked (for obvious reasons) at modification operations and results in a validation error. This can be set to `True`, `False`

    - `collection` (default: `False`) — attribute is to be treated as a collection. This means that the response body will always be at least an array of one and any operations (such as pagination) that are defined for collections are defined for it.

 - Added `name` parameter to attributes to override name in resource model (normally derived from the python name).

 - Added simple path traversal for attributes (eg. `GET /path/attribute` or `GET /path/slug/attribute`).
