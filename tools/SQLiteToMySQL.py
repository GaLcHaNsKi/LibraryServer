from db_client import cursor as mysql, connection
from sqlite3 import connect

sqlite = connect("../app.db").cursor()

# libraries
sqlite.execute("select name from libraries")
libraries = sqlite.fetchall()

for library in libraries:
    mysql.execute(f"insert into libraries (name) values ({library[0]})")

# users
sqlite.execute("select nickname, coded_password, role, is_hired, director_id, library_id, id from users")
users = sqlite.fetchall()

for user in users:
    mysql.execute(f"insert into users values ('{user[0]}', null, '{user[1]}', '{'OWNER' if user[2] == 1 else 'LIBRARIAN'}')")

    if user[2] == 1:
        mysql.execute(f"insert into directors values ({user[-1]}, {user[5]})")
    else:
        mysql.execute(f"insert into librarians values ({user[-1]}, {user[3]}, {user[4]}, {user[5]})")

sqlite.close()
mysql.close()
connection.commit()
connection.close()

if __name__ == "__main__":
    pass
