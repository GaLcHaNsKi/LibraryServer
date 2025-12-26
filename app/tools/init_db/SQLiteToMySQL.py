from tools.init_db.db_client import cursor as mysql, connection
from sqlite3 import connect

sqlite = connect("../../app.db").cursor()

# users
sqlite.execute("select u.nickname, u.coded_password, u.role, u.is_hired, dir.nickname from users u left join users dir on dir.id=u.director_id")
users = sqlite.fetchall()

for user in users:
    if user[2] == 1:
        mysql.execute(f"insert into users (nickname, email, password_hash, role) values ('{user[0]}', null, '{user[1]}', '{'OWNER' if user[2] == 1 else 'LIBRARIAN'}')")
        id = mysql.lastrowid
        mysql.execute(f"insert into directors (user_id) values ({id})")

for user in users:
    if user[2] == 0:
        mysql.execute(f"insert into users (nickname, email, coded_password, role) values ('{user[0]}', null, '{user[1]}', '{'OWNER' if user[2] == 1 else 'LIBRARIAN'}')")
        id = mysql.lastrowid
        mysql.execute(f"insert into librarians (user_id, is_hired, director_id) values ({id}, {user[3]}, (select id from users where nickname='{user[-1]}'))")


# libraries
sqlite.execute("select name from libraries")
libraries = sqlite.fetchall()

for library in libraries:
    mysql.execute(f"insert into libraries (name, director_id) values ('{library[0]}', (select id from users where nickname='{library[0]}'))")
    lib_id = mysql.lastrowid

    mysql.execute(f"update directors set library_id='{lib_id}' where user_id=(select id from users where nickname='{library[0]}')")
    mysql.execute(f"update librarians set library_id='{lib_id}' where director_id=(select id from users where nickname='{library[0]}')")


# books
'''
for library in libraries:
    lib_sql = connect(f"../libraries/{library[0]}/library.db").cursor()
    mysql.execute(f"select id from libraries where name='{library[0]}'")
    id = mysql.fetchone()[0]

    # available
    lib_sql.execute("""select "inventory_num", "title_ru", "title_original", "series",
              "lang_of_book", "lang_original", "author_ru", "author_in_original_lang",
              "writing_year", "transfer_year", "translators", "explanation_ru",
              "applications", "dimensions", "publication_year", "edition_num",
              "publishing_house", "isbn1", "isbn2", "abstract",
              "book_type", "book_genre", "cover_photo", "age_of_reader",
              "quantity", "location", "condition"
            from available_books""")
    for book in lib_sql.fetchall():
        mysql.execute(f"""insert into books (library_id, "inventory_num", "title_ru", "title_original", "series",
              "lang_of_book", "lang_original", "author_ru", "author_in_original_lang",
              "writing_year", "transfer_year", "translators", "explanation_ru",
              "applications", "dimensions", "publication_year", "edition_num",
              "publishing_house", "isbn1", "isbn2", "abstract",
              "book_type", "book_genre", "cover_photo", "age_of_reader",
              "quantity", "location", "condition") values ({id}, ) {(f"'{i}'" for i in book)}""")

    lib_sql.close()
'''

sqlite.close()
connection.commit()
mysql.close()
connection.close()

if __name__ == "__main__":
    pass
