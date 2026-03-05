import json

from werkzeug.wrappers import Request, Response
from app.views.common_service import isExists, InternalErrorResponse, UserNotFoundResponse


class AuthMiddleware:
    def __init__(self, app, flask_app):
        self.app = app
        self.flask_app = flask_app

    def __call__(self, environ, start_response):
        with self.flask_app.app_context():
            request = Request(environ)

            if request.path.startswith(("/index", "/guide", "/apidocs", "/socket.io")) \
                    or request.path == "/favicon.ico" \
                    or "/" == request.path \
                    or request.path.startswith("/static") \
                    or "releases" == request.path.strip("/") \
                    or request.path.startswith("/auth/register"):
                return self.app(environ, start_response)

            res = Response('{"error":"Unauthorized"}', 401, mimetype="application/json")

            auth = request.authorization
            if not auth:
                return res(environ, start_response)

            nickname, password = auth["username"], auth["password"]

            userId = isExists(nickname, password)
            if userId > 0:
                environ["user"] = {"id": userId, "nickname": nickname, "coded_password": password}

                return self.app(environ, start_response)
            elif userId < 0:
                res = Response(json.dumps(InternalErrorResponse[0]), InternalErrorResponse[1], mimetype="application/json")
            elif userId == 0:
                res = Response(json.dumps(UserNotFoundResponse[0]), UserNotFoundResponse[1], mimetype="application/json")

            return res(environ, start_response)
