from flask import render_template, request, send_file
from app import *
import time
from .users_control import *
from .notifications_control import *
from .create_library import create_library
from .library_control import Library
from .libraries_control import *
from .logs import elog, log
from .EncoderDecoder.encoder import encode

from .middleware import middleware

"""
    Возвращаемые значения:
        0 - всё хорошо;
        1 - такого нет среди пользователей (или пароль не тот);
        2 - библиотекарь нанят;
        3 - nickname занят;
        4 - библиотекарь не нанят;
        5 - неизвестная команда;
        6 - ошибка базы данных;
        7 - книг больше нет;
        8 - некоторая ошибка;
        9 - нельзя удалить директора/библиотеку;
        10 - левый пользователь

    Значения параметра cmd:
        "send" - отправить оповещение;
        "read" - прочитал оповещение, удалить;
        "offer" - пригласить на работу;
        "hire" - нанять библиотекаря;
        "dismiss" - уволить бибилиотекаря;

"""
LASTEST_VERSION = "1-6"

app.wsgi_app = middleware(app.wsgi_app)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home", LASTEST_VERSION=LASTEST_VERSION)


@app.route("/guide")
def guide():
    return render_template("guide.html", title="Guide")


@app.route("/releases")
def releases():
    return render_template("releases.html", title="Releases")


@app.route("/releases/<apk>")
def download_apk(apk):
    file = basedir + f"/releases/{apk}"
    return send_file(file, download_name=apk, as_attachment=True)


@app.route("/robots.txt")
def robots():
    return send_file(
        basedir + "/robots.txt",
        mimetype="text/plain"
    )

@app.route("/sitemap.xml")
def sitemap():
    return send_file(
        basedir + "/sitemap.xml",
        mimetype="application/xml"
    )


@app.route("/register", methods=["POST"])
def register():
    """
    Регистрация пользователя. Добавляет в базу данных пользователя, если его nickname ещё нет.
    :return: '3', если nickname уже занят, '0', если пользователь добавлен.
    """
    nickname = request.form["nickname"]
    coded_password = request.form["coded_password"]
    role = request.form["role"]

    status = add_user(nickname, coded_password, role)

    if status == "error":  # ошибка
        return {"status": 6}
    if status == "taken":  # никнейм занят
        return {"status": 3}

    print(f"{nickname} was registered!")

    if role == str(OWNER):
        # если это директор, то создаём библиотеку с его именем
        print("It is director!")
        create_library(nickname)

    return {"status": 0}
    # return render_template("register.html", title="Registration")


@app.route("/login", methods=["GET"])
def login():
    nickname = request.environ["user"]["nickname"]
    print(nickname, "logged in!")

    return {"status": 0, "role": get_role(nickname)}


@app.route("/users", methods=["DELETE"])
def delete_user():
    nickname = request.environ["user"]["nickname"]
    code = del_user(nickname)

    if code == 1:
        return {"status": 6}
    elif code == 2:  # это директор
        return {"status": 9}

    return {"status": 0}


@app.route("/notify", methods=["POST"])
def write_notify():
    author = request.environ["user"]["nickname"]
    recipient = request.form["recipient"]
    title = request.form["title"]
    text = request.form["text"]
    cmd = request.form["cmd"]

    if not is_exists(recipient):
        return {"status": 1}

    if cmd == "send":
        # для записи оповещений
        if send_notify(author, recipient, title, text, "message"):
            return {"status": 6}
    elif cmd == "offer":
        # если директор хочет нанять, то нужно проверить, не нанят ли
        lib_name = is_hired(recipient)
        if lib_name == "":
            if send_notify(author, recipient, title, text, "offer"):
                return {"status": 6}
        elif lib_name == 1:
            return {"status": 6}
        else:
            return {"status": 2}  # т.е., уже нанят

    return {"status": 0}


@app.route("/notify", methods=["DELETE"])
def delete_notify():
    recipient = request.environ["user"]["nickname"]
    author = request.form["author"]
    title = request.form["title"]
    text = request.form["text"]

    if del_notify(author, recipient, title, text):
        return {"status": 6}

    return {"status": 0}


@app.route("/notify", methods=["GET"])
def notify_get():
    # для получения уведомлений
    recipient = request.environ["user"]["nickname"]
    cmd = "get"
    tmp = None
    try:  # для Library < v1.4
        tmp = request.args.get("cmd")
    except:
        pass
    if tmp:
        cmd = tmp

    if cmd == "get":
        ntfs = get_notify(recipient)
        if ntfs == 1:
            return {"status": 6}

        if ntfs != {}:
            ntfs["status"] = 0
            return ntfs
        else:
            return {"status": 7}
    elif cmd == "have":
        res = have_notify(recipient)
        if res < 0:
            return {"status": 6}

        return {"status": 0, "result": res}


@app.route("/librarians", methods=["POST"])
def librarian_control_post():
    """
        Для нанятия и увольнения библиотекарей
    """
    cmd = request.form["cmd"]
    librarian = request.form["librarian"]
    director = request.environ["user"]["nickname"]

    director_id = getUserIDByNickname(director)

    if not is_exists(librarian):
        return {"status": 1}

    code = 0
    if cmd == "hire":
        lib_name = is_hired(librarian)
        if lib_name == 1:
            return {"status": 6}
        elif lib_name != "":
            return {"status": 2}  # т.е., уже нанят

        code = hire_librarian(director_id, librarian)

        print(f"{librarian} hired by {director}")

        send_notify(librarian, director, f"{librarian} теперь с вами!", f"{librarian} присоединился к вам.",
                    "send")
    elif cmd == "dismiss":
        code = dismiss_librarian(librarian)

        send_notify(director, librarian, "Вы уволены!", f"{director} вас уволил.", "send")
        print(f"{librarian} dismissed by {director}")

    if code:
        return {"status": 6}

    return {"status": 0}


@app.route("/librarians", methods=["GET"])
def librarian_control_get_list():
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    lib_list = get_list_of_librarians(director_id)
    if lib_list == 1:
        return {"status": 8}

    lib_list["status"] = 0

    return lib_list


@app.route("/library", methods=["POST"])
def library_control_post():
    librarian = request.environ["user"]["nickname"]
    inventory_num = request.form["inventory_num"]
    cmd = request.form["cmd"]

    lib_name = is_hired(librarian)

    if lib_name == "":
        return {"status": 4}
    elif lib_name == 1:
        return {"status": 6}

    path_to_ldb = basedir + f"libraries/{lib_name.strip()}/library.db"
    lib = Library(path_to_ldb)

    code = 0

    if cmd == "add_book":
        o = request.form["title_original"]
        r = request.form["title_ru"]

        code = lib.add_book(inventory_num=inventory_num,
                            title_ru=r,
                            title_original=o,
                            series=request.form["series"],
                            lang_of_book=request.form["lang_of_book"],
                            lang_original=request.form["lang_original"],
                            author_ru=request.form["author_ru"],
                            author_in_original_lang=request.form["author_in_original_lang"],
                            writing_year=request.form["writing_year"] if request.form[
                                                                             "writing_year"] != "" else "0",
                            transfer_year=request.form["transfer_year"] if request.form[
                                                                               "transfer_year"] != "" else "0",
                            translators=request.form["translators"],
                            explanation_ru=request.form["explanation_ru"],
                            applications=request.form["applications"],
                            dimensions=request.form["dimensions"],
                            publication_year=request.form["publication_year"] if request.form[
                                                                                     "publication_year"] != "" else "0",
                            edition_num=request.form["edition_num"] if request.form[
                                                                           "edition_num"] != "" else "0",
                            publishing_house=request.form["publishing_house"],
                            isbn1=request.form["isbn1"] if request.form["isbn1"] != "" else "0",
                            isbn2=request.form["isbn2"] if request.form["isbn2"] != "" else "0",
                            abstract=request.form["abstract"],
                            book_type=request.form["book_type"],
                            book_genre=request.form["book_genre"],
                            cover_photo=request.form["cover_photo"],
                            age_of_reader=request.form["age_of_reader"],
                            quantity=request.form["quantity"] if request.form["quantity"] != "" else "0",
                            location=request.form["location"],
                            condition=request.form["condition"]
                            )
        log(f'Book "{r if r else o}" added.')
    elif cmd == "move_book":
        name = ""
        dl = ""
        to_tbl = request.form["to_tbl"]
        if to_tbl == "onhands_books":
            name = request.form["name"]
            dl = request.form["deadline"]
        code = lib.move_book(inventory_num=inventory_num, from_tbl=request.form["from_tbl"], to_tbl=to_tbl,
                             name=name, deadline=dl)
    elif cmd == "delete_book":
        code = lib.delete_book(inventory_num=inventory_num, from_tbl=request.form["from_tbl"])
        lib.delete_book_from_deleted(inventory_num)
    elif cmd == "restore_book":
        code = lib.restore_book(inventory_num)
    elif cmd == "delete_book_from_deleted":
        code = lib.delete_book_from_deleted(inventory_num)
    elif cmd == "edit_book":
        # получаем строки со списком изменённых полей и их значений
        str_fields = request.form["fields_to_change"]
        str_values = request.form["new_values"]
        # преобразуем в tuple
        ftc = tuple(str_fields.split(","))
        nv = tuple(str_values.split(","))
        code = lib.edit_book(table=request.form["table"], inventory_num=inventory_num, fields_to_change=ftc,
                             new_values=nv)

    del lib

    if code:
        return {"status": 6}

    return {"status": 0}


@app.route("/library", methods=["GET"])
def library_control_get():
    librarian = request.environ["user"]["nickname"]
    cmd = request.args.get("cmd")
    filter_ = request.args.get("filter")

    lib_name = is_hired(librarian)

    if lib_name == "":
        return {"status": 4}
    elif lib_name == 1:
        return {"status": 6}

    path_to_ldb = basedir + f"libraries/{lib_name.strip()}/library.db"

    lib = Library(path_to_ldb)
    tbl = request.args.get("table")

    if cmd == "get_m_rows_from_n":
        books = lib.get_m_rows_from_n(table=tbl, m=request.args.get("m"), n=int(request.args.get("n")),
                                      filter_=filter_)
        if books == 1:
            return {"status": 6}
        elif not books:
            return {"status": 7}

        ret_books = {}
        i = 0
        for b in books:
            i += 1
            tmp = {}
            for f_j, field in enumerate(lib.base_fields):
                tmp[field] = b[f_j]

            ret_books[str(i)] = tmp

        ret_books["status"] = 0
        ret_books["quantity"] = i

        return ret_books

    elif cmd == "get_one":
        tbl = request.args.get("table")
        inv_num = request.args.get("inventory_num")
        b = lib.get_one(tbl, inv_num)

        if b == 1:
            return {"status": 6}
        if not b:
            return {"status": 7}

        ret_book = {}
        if tbl != "autofill_table":
            for f_j, field in enumerate(lib.fields):
                ret_book[field] = b[f_j]

            if tbl == "onhands_books":
                ret_book["name"] = b[27]
                ret_book["deadline"] = b[28]
        else:
            for f_j, field in enumerate(lib.common_fields):
                ret_book[field] = b[f_j]

        ret_book["status"] = 0

        return ret_book
    else:
        return {"status": 5}


@app.route("/library/places", methods=["GET"])
def sendPlacesList():
    librarian = request.environ["user"]["nickname"]
    lib_name = is_hired(librarian)

    if lib_name == "":
        return {"status": 4}
    elif lib_name == 1:
        return {"status": 6}

    path_to_ldb = basedir + f"libraries/{lib_name.strip()}/library.db"

    # lib = Library(path_to_ldb)
    places_list = Library(path_to_ldb).get_places_list()

    if places_list == 1:
        return {"status": 6}

    return {"status": 0, "locations_list": places_list}


@app.route("/library", methods=["DELETE"])
def delete_library():
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    if get_role(director) != OWNER:
        return {"status": 10}

    librarians = get_list_of_librarians(director_id)

    if delLibraryByDirectorID(director_id):
        return {"status": 6}

    # оповещение библиотекарям
    for i in range(1, librarians["quant"] + 1):
        send_notify(director, librarians[str(i)], "Вы уволены!", f"{director} вас уволил.", "send")

    return {"status": 0}


@app.route("/library/transfer", methods=["PUT"])
def transfer_library():
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    successor = request.form["successor"]
    successor_id = is_exists(successor)

    if not successor_id:
        return {"status": 1}

    code = transferLibrary(director_id, successor_id)

    if code == 1:
        return {"status": 6}
    elif code == 2:
        return {"status": 10}

    # оповещение библиотекарям
    librarians = get_list_of_librarians(successor_id)
    for i in range(1, librarians["quant"] + 1):
        send_notify(director, librarians[str(i)], "У вас новый директор!",
                    f"{director} передал свою библиотеку пользователю {successor}.", "send")

    return {"status": 0}


@app.route("/library/check_deadline", methods=["POST"])
def check_deadline():
    """
        Для записи уведомлений о пропущенных сроках возврата книг
    """
    librarian = request.environ["user"]["nickname"]
    date = request.form["date"]

    lib_name = is_hired(librarian)

    if lib_name == "":
        return {"status": 4}
    elif lib_name == 1:
        return {"status": 6}

    path_to_ldb = basedir + f"libraries/{lib_name.strip()}/library.db"

    lib = Library(path_to_ldb)
    lib.db_curs.execute("select * from onhands_books")
    books = lib.db_curs.fetchall()

    del lib

    for book in books:
        try:
            wdate = time.strptime(book[-1], "%d.%m.%Y")
            ndate = time.strptime(date, "%d.%m.%Y")
            if wdate <= ndate:
                if send_notify("Library", librarian, "Книга не возвращена вовремя!",
                               f"{book[-2]} не вернул \"{book[1] if book[1] != '' else book[2]}\" вовремя!",
                               "message"):
                    return {"status": 6}
        except Exception as e:
            elog(e, file="views", line=459)
            return {"status": "IncorrectDateFormat"}

    return {"status": 0}


@app.route("/library/autofill", methods=["GET"])
def autofill():
    librarian = request.environ["user"]["nickname"]

    lib_name = is_hired(librarian)

    if lib_name == "":
        return {"status": 4}
    elif lib_name == 1:
        return {"status": 6}

    field = request.args.get("field")
    value = request.args.get("value")

    # список директоров
    dir_list = get_list_of_directors()
    if dir_list == 1:
        return {"status": 6}

    # подготовка автозаполнения
    path_to_ldb = basedir + f"libraries/{lib_name.strip()}/library.db"
    lib = Library(path_to_ldb)
    lib.clear_autofill_table()

    is_find = False
    for director in dir_list:
        dlib_name = is_hired(director)
        if dlib_name == 1:
            continue

        dlib = Library(basedir + f"libraries/{dlib_name.strip()}/library.db")

        for t in (lib.tables[0], lib.tables[1]):
            all_dlibrary_books = dlib.find_by_field_value(field, value, table=t)

            if all_dlibrary_books == 1 or all_dlibrary_books == []:
                continue

            is_find = True
            for book in all_dlibrary_books:
                lib.add_to_autofill_table(values=book)

        del dlib
    del lib

    if not is_find:
        return {"status": 7}

    return {"status": 0}


################################################################################
# for Rick

@app.route("/for_ricks_db/insert", methods=["POST"])
def insert_into():
    table = request.form["table"]
    query = "insert into " + table
    if table == "client_rent":
        # Клиент по аренде
        name = request.form["name"]
        who = request.form["who"]
        phone = request.form["number"]
        entrance = request.form["entrance"]
        exit_ = request.form["exit"]

        query += f" (name, who, number, entrance, exit) values ('{name}', '{who}', '{phone}', '{entrance}', '{exit_}')"
    elif table == "employee_ent":
        # Время входа
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]

        query += f" (name, date, time) values ('{name}', '{date}', '{time}')"
    elif table == "employee_left":
        # Время выхода
        name = request.form["name"]
        where = request.form["where_left"]
        time = request.form["time"]

        query += f" (name, where_left, time) values ('{name}', '{where}', '{time}')"
    else:
        # Сдано
        id = request.form["id"]
        date = request.form["date"]
        phone = request.form["number"]

        query += f" (id, date, number) values ('{id}', '{date}', '{phone}')"

    db = connect(basedir + "app/company.db")
    dbr = connect(basedir + "app/company_recovery.db")

    code = 0
    try:
        db.execute(query)
        dbr.execute(query)
        log(f"Insertion in {table}: " + query)
    except Exception as e:
        elog(e, file="views", line=522)
        code = 1

    db.commit()
    dbr.commit()

    db.close()
    dbr.close()

    return str(code)


@app.route("/for_ricks_db/check_password", methods=["POST"])
def check_password(user="", passw=""):
    # если result == 1, то такой пользователь есть
    if not passw:
        passw = encode(request.form["password"])[0]
    else:
        passw = encode(passw)[0]
    if not user:
        user = request.form["user"]
    db = connect(basedir + "app/company.db")
    db_curs = db.cursor()
    code = 0
    res = 0
    try:
        db_curs.execute(f"select * from users where user='{user}' and password='{passw}'")
        data = db_curs.fetchall()
        if len(data) == 1:
            res = 1
    except Exception as e:
        elog(e, file="views", line=546)
        code = 1
    db.close()
    return {"code": code, "result": res}


def create_html_table(rows, headers):
    # Открываем тег <table>
    table_html = "<table>"
    # Добавляем заголовки столбцов
    table_html += "<tr>"
    for header in headers:
        table_html += f"<th>{header}</th>"
    table_html += "</tr>"
    # Добавляем строки данных
    for row in rows:
        table_html += "<tr>"
        for cell in row:
            table_html += f"<td>{cell if cell != None else ''}</td>"
        table_html += "</tr>"
    # Закрываем тег <table>
    table_html += "</table>"
    return table_html


@app.route("/for_ricks_db/read_table", methods=["POST"])
def read_table():
    table_name = request.form["table"]
    passw = request.form["password"]
    user = request.form["user"]

    if user != "admin":
        return {"code": 3}  # только для админов

    cp = check_password(user, passw)

    if cp["code"] == 1:
        return {"code": 1, "table": ""}
    if cp["result"] == 0:
        return {"code": 2, "table": ""}

    headers = ["No"]
    if table_name == "client_rent":
        # Клиент по аренде
        headers += ["Имя", "Чей клиент", "Телефон", "Вход", "Выход"]
    elif table_name == "employee_ent":
        # Время входа
        headers += ["Имя", "Дата", "Время"]
    elif table_name == "employee_left":
        # Время выхода
        headers += ["Имя", "Куда", "Время"]
    else:
        # Сдано
        headers += ["ID", "Дата", "Телефон"]
    db = connect(basedir + "app/company.db")
    db_curs = db.cursor()
    html_table = ""
    code = 0
    try:
        db_curs.execute("select * from " + table_name)
        data = db_curs.fetchall()
        html_table = create_html_table(data, headers)
        log("Readed table: " + table_name)
    except Exception as e:
        elog(e, file="views", line=604)
        code = 1
    db.close()
    return {"code": code, "table": html_table}


@app.route("/for_ricks_db/delete_row", methods=["POST"])
def delete_row():
    table = request.form["table"]
    passw = request.form["password"]
    user = request.form["user"]

    if user != "admin":
        return {"code": 3}  # только для админов

    cp = check_password(user, passw)

    if cp["code"] == 1:
        return "1"
    if cp["result"] == 0:
        return {"status": "2"}

    id = request.form["id"]
    db = connect(basedir + "app/company.db")
    code = 0
    try:
        db.execute(f"delete from {table} where NO={id}")
        log(f"Deleting from {table}. NO={id}")
    except Exception as e:
        elog(e, file="views", line=628)
        code = 1
    db.commit()
    db.close()
    return str(code)


@app.route("/for_ricks_db/edit_row", methods=["POST"])
def edit_row():
    passw = request.form["password"]
    user = request.form["user"]

    if user != "admin":
        return {"code": 3}  # только для админов

    cp = check_password(user, passw)

    if cp["code"] == 1:
        return "1"
    if cp["result"] == 0:
        return {"status": "2"}

    table_name = request.form["table"]
    NO = request.form["NO"]

    query = f"update {table_name} set "

    if table_name == "client_rent":
        # Клиент по аренде
        name = request.form["name"]
        who = request.form["who"]
        phone = request.form["number"]
        entrance = request.form["entrance"]
        exit_ = request.form["exit"]

        query += f"name='{name}', who='{who}', number='{phone}', entrance='{entrance}', exit='{exit_}'"
    elif table_name == "employee_ent":
        # Время входа
        name = request.form["name"]
        date = request.form["date"]
        time = request.form["time"]

        query += f"name='{name}', date='{date}', time='{time}'"
    elif table_name == "employee_left":
        # Время выхода
        name = request.form["name"]
        where = request.form["where_left"]
        time = request.form["time"]

        query += f"name='{name}', where_left='{where}', time='{time}'"
    else:
        # Сдано
        id = request.form["id"]
        date = request.form["date"]
        phone = request.form["number"]

        query += f"id={id}, date='{date}', number='{phone}'"

    query += f" where NO={NO}"

    db = connect(basedir + "app/company.db")
    dbr = connect(basedir + "app/company_recovery.db")

    code = 0
    try:
        db.execute(query)
        dbr.execute(query)
        log(f"Editing {table_name}. NO={NO}. Query: {query}")
    except Exception as e:
        elog(e, file="views", line=682)
        code = 1

    db.commit()
    dbr.commit()

    db.close()
    dbr.close()
    return str(code)


@app.route("/for_ricks_db/export_db", methods=["GET"])
def download_db():
    passw = request.args.get("password")
    user = request.args.get("user")

    if user != "admin":
        return {"code": 3}  # только для админов

    cp = check_password(user, passw)

    if cp["code"] == 1:
        return {"code": 1}
    if cp["result"] == 0:
        return {"code": 2}

    path = basedir + "app/company.db"
    return send_file(path, download_name="taj_residence.db", as_attachment=True)


@app.route("/for_ricks_db/clear_db", methods=["GET"])
def clear_db():
    passw = request.args.get("password")
    user = request.args.get("user")

    if user != "admin":
        return {"code": 3}  # только для админов

    cp = check_password(user, passw)

    if cp["code"] == 1:
        return {"code": 1}
    if cp["result"] == 0:
        return {"code": 2}
    code = 0
    try:
        from .company_db_tools import clear_all
        clear_all.clear_all(basedir + "app/company.db")
    except Exception as e:
        elog(e, file="views", line=729)
        code = 1
    return {"code": code}

################################################################################
