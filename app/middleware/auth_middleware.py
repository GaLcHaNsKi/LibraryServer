import json

from werkzeug.wrappers import Request, Response

from app import app
from app.views.common_service import isExists, InternalErrorResponse


class auth_middleware():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        with app.app_context():
            request = Request(environ)

            if request.path in ["/", "/index", "/guide"] \
                    or "static" in request.path \
                    or "for_ricks_db" in request.path \
                    or "releases" in request.path \
                    or "register" in request.path:
                return self.app(environ, start_response)

            res = Response('{"error":"Unauthorized"}', 401, mimetype="application/json")

            auth = request.authorization
            if not auth:
                return res(environ, start_response)

            nickname, password = auth["username"], auth["password"]

            id = isExists(nickname, password)
            if id > 0:
                environ["user"] = {"id": id, "nickname": nickname, "coded_password": password}
                return self.app(environ, start_response)
            elif id < 0:
                res = Response(InternalErrorResponse, 500, mimetype="application/json")

            return res(environ, start_response)
