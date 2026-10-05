from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.exceptions import BadRequest
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

OWNER = DIRECTOR = "OWNER"
LIBRARIAN = "LIBRARIAN"
READER = "READER"

ROLES = [OWNER, LIBRARIAN, READER]

basedir = os.path.abspath(os.path.dirname(__file__))[0:-3]

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_BYTES', 5 * 1024 * 1024))
app.config['REQUIRE_HTTPS'] = os.getenv('REQUIRE_HTTPS', '1') == '1'
app.config['TRUST_PROXY_HEADERS'] = os.getenv('TRUST_PROXY_HEADERS', '0') == '1'

# A public API must not silently trust any web origin.  Add the exact origins of
# the web client in production, for example: https://app.example.org
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
app.config['CORS_ALLOWED_ORIGINS'] = allowed_origins

app.url_map.strict_slashes = False

app.config.from_object("config_wtf")
CORS(app, resources={r"/*": {"origins": allowed_origins}})
    
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.errorhandler(BadRequest)
def handle_bad_request(_error):
    """Keep malformed API requests JSON-shaped instead of returning Flask HTML."""
    return {"error": "Invalid or missing request data"}, 400


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    # This site only serves its own templates and static assets.
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' https://*.dropboxusercontent.com https://*.dropbox.com; "
        "style-src 'self'; base-uri 'self'; frame-ancestors 'none'"
    )
    if os.getenv("ENABLE_HSTS", "0") == "1":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

"""
    Для запуска сервера:
    flask run --host=0.0.0.0 --debug
    Для создания миграции:
    flask db migrate -m "Initialize DB"
    flask db upgrade
"""

from app import models
from app import views
from app.tools.init_db.fill_reference_tables import fillReferenceTables

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Library API",
        "description": "API documentation for LibraryServer",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "basicAuth": {
            "type": "basic"
        }
    }
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": os.getenv("ENABLE_SWAGGER_UI", "0") == "1",
    "specs_route": "/apidocs/",
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

with app.app_context():
    fillReferenceTables()

# --- Фоновые задачи (кроны) ---
# Do not run an in-process scheduler in every WSGI worker: that produces
# duplicate notifications. Start it in one dedicated process instead
# (``python run_scheduler.py``), or explicitly opt in for local development.
if os.environ.get("RUN_SCHEDULER", "0") == "1":
    from app.scheduler import start_schedulers

    start_schedulers()
