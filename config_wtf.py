import os

CSRF_ENABLED = True
SECRET_KEY = "Подарил-нам-Создатель-лета-добрую-пору"

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(basedir, "app.db")
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")

