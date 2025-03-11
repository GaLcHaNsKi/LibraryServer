from werkzeug.wrappers import Request, Response
from app.users_control import is_exists1


class middleware():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)

        if request.path in ["/", "/index", "/guide", "/register"] \
                or "static" in request.path \
                or "for_ricks_db" in request.path \
                or "releases" in request.path:
            return self.app(environ, start_response)

        res = Response('{"status": 1}', mimetype="text/plain")

        auth = request.authorization
        if not auth:
            return res(environ, start_response)

        nickname, password = auth["username"], auth["password"]

        if is_exists1(nickname, password):
            environ["user"] = {"nickname": nickname, "coded_password": password}
            return self.app(environ, start_response)

        return res(environ, start_response)
