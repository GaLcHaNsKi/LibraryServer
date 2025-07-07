# TODO: переделать это в крон задачу
'''@libraryBlueprint.route("/check-deadline", methods=["POST"])
def check_deadline():
    """
        Для записи уведомлений о пропущенных сроках возврата книг
    """
    librarian = request.environ["user"]["nickname"]
    date = request.form["date"]

    lib_name = isHired(librarian)

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
            elog(e, file="", line=459)
            return {"status": "IncorrectDateFormat"}

    return {"status": 0}'''
