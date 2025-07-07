from app import app
from tools.init_db.create_db_app import create

if __name__ == "__main__":
    create()
    app.run(host="0.0.0.0")
