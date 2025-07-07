# for Rick
from sqlite3 import connect

from flask import Blueprint, request, send_file

from app import basedir
from app.EncoderDecoder.encoder import encode
from app.views.logs import log, elog

rickBlueprint = Blueprint("rick", __name__)

@rickBlueprint.route("/for_ricks_db/insert", methods=["POST"])
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

    db = connect(basedir + "rickBlueprint/company.db")
    dbr = connect(basedir + "rickBlueprint/company_recovery.db")

    code = 0
    try:
        db.execute(query)
        dbr.execute(query)
        log(f"Insertion in {table}: " + query)
    except Exception as e:
        elog(e, file="", line=522)
        code = 1

    db.commit()
    dbr.commit()

    db.close()
    dbr.close()

    return str(code)


@rickBlueprint.route("/for_ricks_db/check_password", methods=["POST"])
def check_password(user="", passw=""):
    # если result == 1, то такой пользователь есть
    if not passw:
        passw = encode(request.form["password"])[0]
    else:
        passw = encode(passw)[0]
    if not user:
        user = request.form["user"]
    db = connect(basedir + "rickBlueprint/company.db")
    db_curs = db.cursor()
    code = 0
    res = 0
    try:
        db_curs.execute(f"select * from users where user='{user}' and password='{passw}'")
        data = db_curs.fetchall()
        if len(data) == 1:
            res = 1
    except Exception as e:
        elog(e, file="", line=546)
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


@rickBlueprint.route("/for_ricks_db/read_table", methods=["POST"])
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
    db = connect(basedir + "rickBlueprint/company.db")
    db_curs = db.cursor()
    html_table = ""
    code = 0
    try:
        db_curs.execute("select * from " + table_name)
        data = db_curs.fetchall()
        html_table = create_html_table(data, headers)
        log("Readed table: " + table_name)
    except Exception as e:
        elog(e, file="", line=604)
        code = 1
    db.close()
    return {"code": code, "table": html_table}


@rickBlueprint.route("/for_ricks_db/delete_row", methods=["POST"])
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
    db = connect(basedir + "rickBlueprint/company.db")
    code = 0
    try:
        db.execute(f"delete from {table} where NO={id}")
        log(f"Deleting from {table}. NO={id}")
    except Exception as e:
        elog(e, file="", line=628)
        code = 1
    db.commit()
    db.close()
    return str(code)


@rickBlueprint.route("/for_ricks_db/edit_row", methods=["POST"])
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

    db = connect(basedir + "rickBlueprint/company.db")
    dbr = connect(basedir + "rickBlueprint/company_recovery.db")

    code = 0
    try:
        db.execute(query)
        dbr.execute(query)
        log(f"Editing {table_name}. NO={NO}. Query: {query}")
    except Exception as e:
        elog(e, file="", line=682)
        code = 1

    db.commit()
    dbr.commit()

    db.close()
    dbr.close()
    return str(code)


@rickBlueprint.route("/for_ricks_db/export_db", methods=["GET"])
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

    path = basedir + "rickBlueprint/company.db"
    return send_file(path, download_name="taj_residence.db", as_attachment=True)


@rickBlueprint.route("/for_ricks_db/clear_db", methods=["GET"])
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
        clear_all.clear_all(basedir + "rickBlueprint/company.db")
    except Exception as e:
        elog(e, file="", line=729)
        code = 1
    return {"code": code}
