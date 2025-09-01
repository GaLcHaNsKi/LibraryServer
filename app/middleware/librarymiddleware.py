import json

from flask import Response
from werkzeug.wrappers import Request
from app.views.common_service import UserNotFoundResponse, InternalErrorResponse, LibrarianNotHiredResponse
from app.views.users.users_service import isHired


class LibraryMiddleware:
    def __init__(self, app, flask_app):
        self.flask_app = flask_app
        self.app = app

    def __call__(self, environ, start_response):
        with self.flask_app.app_context():
            request = Request(environ)

            if "library" not in request.path:
                return self.app(environ, start_response)

            librarian = environ["user"]["nickname"]
            library = isHired(librarian)

            if library == 1:
                response = Response(json.dumps(UserNotFoundResponse[0]), UserNotFoundResponse[1], mimetype="application/json")
                return response(environ, start_response)
            if library == 2:
                response = Response(json.dumps(InternalErrorResponse[0]), InternalErrorResponse[1], mimetype="application/json")
                return response(environ, start_response)
            elif library == "":
                response = Response(json.dumps(LibrarianNotHiredResponse[0]), LibrarianNotHiredResponse[1], mimetype="application/json")
                return response(environ, start_response)

            environ["user"]["library"] = library

            return self.app(environ, start_response)
