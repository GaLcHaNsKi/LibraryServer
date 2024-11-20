from app import app
from create_db_app import create

if __name__ == "__main__":
    create()
    app.run()