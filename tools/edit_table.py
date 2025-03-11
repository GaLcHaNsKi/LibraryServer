from sqlite3 import connect

db = connect("../app.db")

# db.execute("alter table libraries add constraint lib_name Unique(name)")
# db.execute("alter table users add library_id INTEGER")
'''
curs = db.cursor()
curs.execute("select * from users")
users = curs.fetchall()

for user in users:
    dir_nick = user[5]

    if dir_nick == "":
        continue

    curs.execute(f"select id from users where nickname='{dir_nick}'")
    dir_id = curs.fetchone()[0]

    print(dir_nick, dir_id)

    db.execute(f"update users set director_id={dir_id} where id={user[0]}")
'''
db.executescript("""
CREATE TABLE IF NOT EXISTS new_libraries (
                id INTEGER PRIMARY KEY,
                name TEXT,
                director_id INTEGER,
                Unique(name)
);

INSERT INTO new_libraries (id, name, director_id)
SELECT id, name, director_id
FROM libraries;

DROP TABLE libraries;

ALTER TABLE new_libraries RENAME TO libraries;
""")

db.commit()
db.close()
