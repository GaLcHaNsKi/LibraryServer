from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_socketio import SocketIO
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
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode="threading")


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
from app import sockets
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
# Планировщик стартует вместе с приложением, поэтому кроны работают при любом
# способе запуска сервера (python run.py, flask run, gunicorn, WSGI и т.п.).
# Чтобы запускать кроны отдельно/вручную — отключите автостарт: DISABLE_CRONS=1
if os.environ.get("DISABLE_CRONS", "0") != "1":
    from app.scheduler import start_schedulers

    start_schedulers()
