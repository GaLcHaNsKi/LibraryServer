from sqlite3 import connect

sqlite = connect("../../app.db").cursor()

sqlite.execute("select name from libraries")
libraries = sqlite.fetchall()

# books
for library in libraries:
    print(library[0])
    lib_sql = connect(f"../../libraries/{library[0].strip()}/library.db").cursor()

    q = 0

    lib_sql.execute("select title_ru, book_genre, book_type, location, condition from available_books")
    print("title_ru, book_genre, book_type, location, condition")
    for book in lib_sql.fetchall():
        print(book)
        q += 1

    print(f"Total: {q}")


    lib_sql.close()