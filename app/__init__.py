from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
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

app.url_map.strict_slashes = False

app.config.from_object("config_wtf")
CORS(app, resources={r"/*": {"origins": "*"}})
    
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

with app.app_context():
    fillReferenceTables()
