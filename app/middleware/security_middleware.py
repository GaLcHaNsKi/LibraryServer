"""Small, dependency-free request protections for the HTTP API.

The limiters are deliberately per-process.  Deployments with multiple workers
must also enforce equivalent limits at the reverse proxy / API gateway.
"""
from collections import defaultdict, deque
from threading import Lock
from time import monotonic
import json

from werkzeug.wrappers import Request, Response


class SecurityMiddleware:
    def __init__(self, app, flask_app):
        self.app = app
        self.flask_app = flask_app
        self._requests = defaultdict(deque)
        self._lock = Lock()

    @staticmethod
    def _response(message, status):
        return Response(json.dumps({"error": message}), status, mimetype="application/json")

    def _is_limited(self, key, limit, window_seconds=60):
        now = monotonic()
        with self._lock:
            history = self._requests[key]
            while history and history[0] <= now - window_seconds:
                history.popleft()
            if len(history) >= limit:
                return True
            history.append(now)
            return False

    def __call__(self, environ, start_response):
        request = Request(environ)
        client = environ.get("REMOTE_ADDR", "unknown")
        path = request.path

        request_scheme = request.scheme
        request_host = request.host
        if self.flask_app.config["TRUST_PROXY_HEADERS"]:
            request_scheme = request.headers.get("X-Forwarded-Proto", request_scheme).split(",", 1)[0].strip()
            request_host = request.headers.get("X-Forwarded-Host", request_host).split(",", 1)[0].strip()

        if self.flask_app.config["REQUIRE_HTTPS"] and request_scheme != "https":
            return self._response("HTTPS is required", 403)(environ, start_response)

        # Protect the whole API, with a tighter bound on credential attempts.
        limit = 10 if path == "/auth/login" else 120
        if self._is_limited((client, path), limit):
            return self._response("Too many requests", 429)(environ, start_response)

        content_length = request.content_length
        if content_length is not None and content_length > self.flask_app.config["MAX_CONTENT_LENGTH"]:
            return self._response("Request body is too large", 413)(environ, start_response)

        # Basic authentication has no CSRF token.  Browsers send Origin on
        # cross-site unsafe requests, so reject foreign origins while retaining
        # compatibility with non-browser/mobile clients that have no Origin.
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("Origin")
            if origin:
                origin = origin.rstrip("/")
                own_origin = f"{request_scheme}://{request_host}".rstrip("/")
                if origin != own_origin and origin not in self.flask_app.config["CORS_ALLOWED_ORIGINS"]:
                    return self._response("Origin is not allowed", 403)(environ, start_response)

        return self.app(environ, start_response)
