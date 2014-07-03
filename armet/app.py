from . import resources, http, encoders


def application(environ, start_response):
    # Create the request wrapper around the environ (to make this at
    # least half-way sane).
    request = http.Request(environ)

    # Return an empty 404 if were accessed at "/" (we don't handle this yet).
    if request.path == "/":
        start_response("404 Not Found", [])
        return [b""]

    try:
        # Attempt to find the resource through the initial path.
        resource_cls = resources._registry[request.path[1:]]

    except KeyError:
        # Return a 404; we don't know what the resource is.
        start_response("404 Not Found", [])
        return [b""]

    # Instantiate the resource class.
    resource = resource_cls()

    # Route the resource appropriately.
    try:
        route = getattr(resource, request.method.lower())
    except AttributeError:
        try:
            route = resource.route
        except AttributeError:
            # Method is not allowed on the resource.
            start_response("405 Method Not Allowed", [])
            return [b""]

    # Dispatch the request.
    data = route(request)

    # Find an available encoder.
    content_type = request.headers.get("Accept", "application/json")
    if content_type == "*/*":
        content_type = "application/json"

    try:
        encode = encoders.find(media_range=content_type)

    except KeyError:
        # Failed to find a matching encoder.
        start_response("406 Not Acceptable", [])
        return [b""]

    # Encode the data.
    text = encode(data)

    # Return a successful response.
    # TODO: We need a way to know the content-type here.. or the encoder
    #       needs to handle pushing the content-type.
    start_response("202 Ok", [("Content-Type", "application/json")])
    return [text.encode("utf-8")]
