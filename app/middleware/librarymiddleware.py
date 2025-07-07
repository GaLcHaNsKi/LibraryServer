from werkzeug.wrappers import Request

from app.views.common_service import InternalErrorResponse
from app.views.users.users_service import isHired


class LibraryMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)

        if "library" not in request.path:
            return self.app(environ, start_response)

        librarian = environ["user"]["nickname"]
        library = isHired(librarian)

        if library == 1:
            return InternalErrorResponse
        elif library == "":
            return {"error": "You are not hired!"}, 403

        environ["user"]["library"] = library

        return self.app(environ, start_response)
