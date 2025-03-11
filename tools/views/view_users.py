from sqlite3 import connect

db = connect("../../app.db")
db_curs = db.cursor()
db_curs.execute("select nickname, coded_password, role, is_hired, director_id, library_id from users")
users = db_curs.fetchall()

#db.execute(f"update users set library_id={user[2]} where id={user[0]}")
#db.commit()

for user in users:
    print(user)

db.close()
if __name__ == "__main__": input()
