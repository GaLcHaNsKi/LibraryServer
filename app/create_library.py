from app import basedir
from app.trash.create_ldb import create_ldb
from os import makedirs

from sqlite3 import connect
from app import DATABASE_PATH


def create_library(nickname):
    path_to_library = basedir + "libraries/" + nickname
    makedirs(path_to_library)
    create_ldb(path_to_db=path_to_library+"/library.db")

    # добавляем запись в libraries
    db = connect(DATABASE_PATH)
    db_curs = db.cursor()

    db_curs.execute(f"select id from users where nickname='{nickname}'")
    user_id = db_curs.fetchone()[0]

    db.execute(f"insert into libraries (name, director_id) values ('{nickname}', {user_id})")

    db_curs.execute(f"select id from libraries where name='{nickname}'")
    lib_id = db_curs.fetchone()[0]

    db.execute(f"update users set library_id={lib_id} where id={user_id}")

    db.commit()
    db.close()

    print(f"I create new library \"{nickname}\"!")