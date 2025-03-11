from flask import Flask
import os

OWNER = DIRECTOR = "OWNER"
LIBRARIAN = "LIBRARIAN"

basedir = os.path.abspath(os.path.dirname(__file__))[0:-3]
DATABASE_PATH = os.path.join(basedir, "app.db")

app = Flask(__name__)
app.config.from_object("config_wtf")

from app import views