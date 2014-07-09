from . import decoders, encoders, http
from armet.http import exceptions
from armet import utils


class Api:

    def __init__(self, trailing_slash=True):
        # TODO: Should this be that `Registry` thing we were talking about?
        #       That would give us the `remove` functionality easily
        self._registry = {}

    def reroute(self, request, response):
        """Reroute the user to the correct URI"""
        response.headers['Location'] = request.path + "/"
        if not request.method == "GET":
            response.status_code = 301
            return
        response.status_code = 307

    def setup(self):
        """Called on request setup in the context of this API.
        """

    def teardown(self):
        """Called on request teardown in the context of this API.
        """

    def register(self, handler, *, expose=True, name=None): # noqa
        # Discern the name of the handler in order to register it.
        if name is None:
            # Convert the name of the handler to dash-case
            name = utils.dasherize(handler.__name__)

            # Strip a trailing '-resource' from it
            if name.endswith("-resource"):
                name = name[:-9]

        # Insert the handler into the registry.
        self._registry[name] = handler

    def __call__(self, environ, start_response):
        """Entry-point from the WSGI environment.

        When a request comes in from a "client" this is the first place
        it goes after it is received by the "server" (uWSGI, nginx, etc.).
        """

        # Create the request and response wrappers around the environ.
        request = http.Request(environ)
        response = http.Response()

        if not self.trailing_slash:
            self.reroute(request, response)
            return response(environ, start_response)
        # Setup the request.
        self.setup()

        # Route the request.. needs a better name for the function perhaps.
        try:
            self.route(request, response)

        except Exception as ex:
            response.status_code = ex.status
			response.set_data(b"")

        # Teardown the request.
        # FIXME: This should happen directly before closing the connection
        #        with the user, not here.
        self.teardown()

        # Invoke the response wrapper to initiate the (possibly streaming)
        # response.
        return response(environ, start_response)

    def get_resource(self, path):
        return self._registry[path]

    def route(self, request, response):
        # TODO: We need a way to know the content-type here.. or the encoder
        #       needs to handle pushing the content-type.

        # Return an empty 404 if were accessed at "/" (
        # we don't handle this yet).
        if request.path == "/":
            raise exceptions.NotFound()

        name_slug_pair = utils.split_url(request.path)

        # TODO: Iterate through each pair in the sequence

        resource_classes = []

        try:
            # Attempt to find the resource through the initial path.
            for pair in name_slug_pair:
                # pair is a tuple containing the name and slug,
                # ("poll", 3), (choice, '')
                resource_classes.append(self.get_resource(pair[0]))

        except KeyError:
            # Return a 404; we don't know what the resource is.
            raise exceptions.NotFound()

        # Instantiate the resource classes.
        for resource in resource_classes:
            resource(request=request)

            # Route the resource appropriately.
            try:
                route = getattr(resource, request.method.lower())

            except AttributeError:
                try:
                    route = resource.route

                except AttributeError:
                    # Method is not allowed on the resource.
                    raise exceptions.MethodNotAllowed()

        # Read in the request data.
        # TODO: Think of a way to expose this (just "content" or "data")
        request_raw_data = request._handle.data
        request_data = None
        if request_raw_data:
            # Find an available decoder.
            content_type = request.headers.get("Content-Type")
            if not content_type:
                # TODO: Handle content-type "detection"
                raise exceptions.UnsupportedMediaType()

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
                raise exceptions.UnsupportedMediaType()
                return

        # Dispatch the request.
        response_data = route(request_data)

        # Find an available encoder.
        media_range = request.headers.get("Accept", "application/json")
        if media_range == "*/*":
            media_range = "application/json"

        try:
            encoder = encoders.find(media_range=media_range)

            # Encode the data.
            # TODO: We should be detecting the proper charset and using that
            # instead.
            response.response = encoder(response_data, 'utf-8')
            response.headers['Content-Type'] = encoder.preferred_mime_type

        except (KeyError, TypeError):
            # Failed to find a matching encoder.
            response.status_code = exceptions.NotAcceptable()
            return

        # Return a successful response.
        response.status_code = 200
        return
