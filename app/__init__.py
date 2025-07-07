from flask import Flask
from flask_cors import CORS
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

OWNER = DIRECTOR = "OWNER"
LIBRARIAN = "LIBRARIAN"
READER = "READER"

ROLES = [OWNER, LIBRARIAN, READER]

basedir = os.path.abspath(os.path.dirname(__file__))[0:-3]
DATABASE_PATH = os.path.join(basedir, "app.db")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
