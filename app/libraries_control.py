from sqlite3 import connect
from app import basedir, DATABASE_PATH, LIBRARIAN, OWNER
from .logs import elog
import os

DATABASE = DATABASE_PATH


def delLibraryByDirectorID(director_id):
    db = connect(DATABASE)
    db_curs = db.cursor()
    try:
        db_curs.execute(f"select id, name from libraries where director_id='{director_id}'")
        library = db_curs.fetchone()

        if not library:
            return 1

        lib_id = library[0]
        # если есть библиотекари, увольняем их, заодно и директора делаем библиотекарем
        db.execute(f"update users set is_hired=0, role={LIBRARIAN}, director_id=null, library_id=null where library_id={lib_id}")
        # удаляем библиотеку
        db.execute(f"delete from libraries where id='{lib_id}'")

        # теперь надо удалить БД
        lib_name = library[1]
        path_to_library = os.path.join(basedir, "libraries", lib_name)

        os.remove(os.path.join(path_to_library, "library.db"))
        os.rmdir(path_to_library)

        db.commit()
    except Exception as e:
        elog(e, file="libraries_control", line=11)
        return 1
    db.close()
    return 0

def transferLibrary(director_id, librarian_id):
    db = connect(DATABASE)
    db_curs = db.cursor()
    try:
        db_curs.execute(f"select id from libraries where director_id='{director_id}'")
        library = db_curs.fetchone()

        if not library:
            return 2 # он не директор этой библиотеки

        db_curs.execute(f"select id from users where director_id={director_id} and id={librarian_id}")
        user = db_curs.fetchone()

        if not user:
            return 2 # пользователь не из этой библиотеки

        # директора делаем библиотекарем
        db.execute(f"update users set role={LIBRARIAN}, director_id={librarian_id}, is_hired=1 where id={director_id}")
        # библиотекаря делаем директором
        db.execute(f"update users set role={OWNER}, director_id=null, is_hired=0 where id={librarian_id}")
        # в libraries устанавливаем новго директора
        db.execute(f"update libraries set director_id={librarian_id} where id={library[0]}")

        # если есть библиотекари, ставим им нового директора
        db.execute(f"update users set director_id={librarian_id} where director_id={director_id}")

        db.commit()

    except Exception as e:
        elog(e, file="libraries_control", line=41)
        return 1
    finally:
        db.close()

    return 0