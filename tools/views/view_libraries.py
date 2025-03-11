from sqlite3 import connect

db = connect("../../app.db")
db_curs = db.cursor()
db_curs.execute("select name, director_id from libraries")#("select lib.*, u.nickname as director from libraries lib join users u on lib.director_id=u.director_id")
libraries = db_curs.fetchall()

# db.execute(f"insert into libraries (name, director_id) values ('{lib[1]}', {lib[0]})")
# db.commit()
# db.close()

for lib in libraries:
    print(lib)


if __name__ == "__main__": input()
