import os
from dotenv import load_dotenv

load_dotenv()

CSRF_ENABLED = True
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(basedir, "app.db")
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")

