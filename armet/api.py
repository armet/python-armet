from . import decoders, encoders, http
import re


def _dasherize(text):
    # TODO: This could probably be optimized significantly.
    text = text.strip()
    text = re.sub(r'([A-Z])', r'-\1', text)
    text = re.sub(r'[-_\s]+', r'-', text)
    text = re.sub(r'^-', r'', text)
    text = text.lower()
    return text.strip()


class Api:

    def __init__(self):
        # TODO: Should this be that `Registry` thing we were talking about?
        #       That would give us the `remove` functionality easily
        self._registry = {}

    def register(self, handler, *, expose=True, name=None):
        # Discern the name of the handler in order to register it.
        if name is None:
            # Convert the name of the handler to dash-case
            name = _dasherize(handler.__name__)

            # Strip a trailing '-resource' from it
            name = re.sub(r'-resource$', '', name)

        # Insert the handler into the registry.
        self._registry[name] = handler

    def __call__(self, environ, start_response):
        # Create the request wrapper around the environ (to make this at
        # least half-way sane).
        request = http.Request(environ)
        response = http.Response()

        self.process(request, response)

        return response(environ, start_response)

    def process(self, request, response):
        # TODO: We need a way to know the content-type here.. or the encoder
        #       needs to handle pushing the content-type.

        # Return an empty 404 if were accessed at "/" (
        # we don't handle this yet).
        if request.path == "/":
            response.status_code = 404
            return

        try:
            # Attempt to find the resource through the initial path.
            resource_cls = self._registry[request.path[1:]]

        except KeyError:
            # Return a 404; we don't know what the resource is.
            response.status_code = 404
            return

        # Instantiate the resource class.
        resource = resource_cls(request=request)

        # Route the resource appropriately.
        try:
            route = getattr(resource, request.method.lower())

        except AttributeError:
            try:
                route = resource.route

            except AttributeError:
                # Method is not allowed on the resource.
                response.status_code = 405
                return

        # Read in the request data.
        # TODO: Think of a way to expose this (just "content" or "data")
        request_raw_data = request._handle.data
        request_data = None
        if request_raw_data:
            # Find an available decoder.
            content_type = request.headers.get("Content-Type")
            if not content_type:
                # TODO: Handle content-type "detection"
                response.status_code = 415
                return

            try:
                # TODO: The content-type header could state more than just
                #       the mime_type (charset, etc.); think of how to deal
                #       with it as media_range detection "works" with it but
                #       mime_type would be faster.
                decode = decoders.find(media_range=content_type)

                # Decode the incoming request data.
                # TODO: We should likely be sending the proper charset
                #       to ".decode(..)"
                request_data = decode(request_raw_data.decode("utf-8"))

            except (KeyError, TypeError):
                # Failed to find a matching encoder.
                response.status_code = 415
                return

        # Dispatch the request.
        response_data = route(request_data)

        # Find an available encoder.
        media_range = request.headers.get("Accept", "application/json")
        if media_range == "*/*":
            media_range = "application/json"

        try:
            encode = encoders.find(media_range=media_range)

            # Encode the data.
            response_text = encode(response_data)

        except (KeyError, TypeError):
            # Failed to find a matching encoder.
            response.status_code = 406
            return

        # Return a successful response.
        response.status_code = 200
        response.headers['Content-Type'] = 'application/json'
        response.data = response_text
        return
