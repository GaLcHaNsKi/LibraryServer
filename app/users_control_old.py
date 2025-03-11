from sqlite3 import connect
from app import DATABASE_PATH, OWNER, LIBRARIAN
from .logs import elog
import hashlib

DATABASE = DATABASE_PATH


def hash_password(password):
    # Преобразуем строку в байты
    password_bytes = password.encode('utf-8')

    # Создаем объект хеширования
    hash_object = hashlib.sha256(password_bytes)

    # Получаем хеш в шестнадцатеричном формате
    hex_dig = hash_object.hexdigest()

    return hex_dig


def add_user(nickname, coded_password, role):
    db = connect(DATABASE)
    db_curs = db.cursor()

    try:
        # выборка всех пользователей с тем же nickname
        db_curs.execute(f"select * from users where nickname='{nickname}'")
        if db_curs.fetchall() == []:
            # если таких ещё нет, то добавляем
            # хешируем пароль
            hash_passw = hash_password(coded_password)

            db.execute(
                f"insert into users (nickname, coded_password, role, is_hired) values ('{nickname}', '{hash_passw}', {role}, 0)")
            db.commit()
        else:
            # если nickname занят
            return "taken"
    except Exception as e:
        elog(e, file="users_control", line=24)
        return "error"
    finally:
        db.close()

    return 0


def del_user(nickname):
    db = connect(DATABASE)
    db_curs = db.cursor()
    try:
        db_curs.execute(f"select role from users where nickname='{nickname}'")
        role = db_curs.fetchone()[0]

        if role == OWNER:  # нельзя удалять директора
            return 2

        db.execute(f"delete from users where nickname='{nickname}'")
        db.commit()
    except Exception as e:
        elog(e, file="users_control", line=49)
        return 1

    db.close()

    return 0


def is_exists1(nickname, coded_password):
    db = connect(DATABASE)
    db_curs = db.cursor()
    user_id = 0
    try:
        db_curs.execute(
            f"select id from users where nickname='{nickname}' and coded_password='{hash_password(coded_password)}'")
        user = db_curs.fetchall()
        if user != []:
            user_id = user[0][0]
    except Exception as e:
        elog(e, file="users_control", line=100)
        return 0

    db.close()

    return user_id


def is_exists(nickname):
    db = connect(DATABASE)
    db_curs = db.cursor()
    user_id = 0
    try:
        db_curs.execute(f"select id from users where nickname='{nickname}'")
        user = db_curs.fetchall()
        if user != []:
            user_id = user[0][0]
    except Exception as e:
        elog(e, file="users_control", line=77)
        return 0
    db.close()
    return user_id


def get_role(nickname):
    db = connect(DATABASE)
    try:
        db_curs = db.cursor()
        db_curs.execute(f"select role from users where nickname='{nickname}'")
        role = db_curs.fetchone()[0]
    except Exception as e:
        elog(e, file="users_control", line=90)
        return -1
    db.close()
    return role


def hire_librarian(director_id, librarian):
    db = connect(DATABASE)
    db_curs = db.cursor()
    try:
        db_curs.execute(f"select library_id from users where id={director_id}")
        lib_id = db_curs.fetchone()[0]

        db.execute(
            f"update users set director_id={director_id}, library_id={lib_id}, is_hired=1 where nickname='{librarian}'")
        db.commit()
    except Exception as e:
        elog(e, file="users_control", line=104)
        return 1
    db.close()
    return 0


def dismiss_librarian(librarian):
    db = connect(DATABASE)
    try:
        db.execute(f"update users set director_id=null, library_id=null, is_hired=0 where nickname='{librarian}'")
        db.commit()
    except Exception as e:
        elog(e, file="users_control", line=81)
        return 1
    db.close()
    return 0


def is_hired(librarian):
    """
    Если librarian - библиотекарь, возвращаем:
        "" - не нанят;
        "library name" - название библиотеки, если нанят.
    Иначе если librarian - директор, возвращается название его библиотеки.
    Если такого нет, или произошла ошибка, возвращаем 1.
    """
    if not is_exists(librarian):
        return 1

    db = connect(DATABASE)
    try:
        db_curs = db.cursor()
        db_curs.execute(f"select is_hired, library_id, role from users where nickname='{librarian}'")
        user = db_curs.fetchone()

        if not user[0] and user[2] == LIBRARIAN:
            return ""

        db_curs.execute(f"select name from libraries where id={user[1]}")

        return db_curs.fetchone()[0]
    except Exception as e:
        elog(e, file="users_control", line=102)
        return 1
    finally:
        db.close()


def getUserIDByNickname(nickname):
    db = connect(DATABASE)
    db_curs = db.cursor()

    db_curs.execute(f"select id from users where nickname='{nickname}'")
    user_id = db_curs.fetchone()[0]

    db.close()

    if not user_id:
        return 0

    return user_id


def get_list_of_librarians(director_id):
    db = connect(DATABASE)
    db_curs = db.cursor()
    code = 0
    lib_list = dict({})
    try:
        db_curs.execute(
            f"select * from users where director_id='{director_id}' and role={LIBRARIAN} order by nickname asc")

        tmp = db_curs.fetchall()
        i = 0
        for n in tmp:
            i += 1
            lib_list[str(i)] = n[1]
        lib_list["quant"] = i
    except Exception as e:
        elog(e, file="users_control", line=147)
        code = 1
    db.close()
    return lib_list if code == 0 else 1


def get_list_of_directors():
    db = connect(DATABASE)
    db_curs = db.cursor()
    code = 0
    dir_list = []
    try:
        db_curs.execute("select * from users where role=1")
        tmp = db_curs.fetchall()
        for n in tmp:
            dir_list += [n[1]]
    except Exception as e:
        elog(e, file="users_control", line=161)
        code = 1
    db.close()
    return dir_list if code == 0 else 1
