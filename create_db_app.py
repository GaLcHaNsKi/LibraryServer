from sqlite3 import connect

DATABASE = "app.db"
db = connect(DATABASE)
def create():
    db.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                nickname TEXT,
                coded_password TEXT,
                role INTEGER,
                is_hired INTEGER,
                director_id INTEGER,
                library_id INTEGER,
                Unique(nickname)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS libraries (
                id INTEGER PRIMARY KEY,
                name TEXT,
                director_id INTEGER,
                Unique(name)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS notifications (
                author TEXT,
                recipient TEXT,
                title TEXT,
                content TEXT,
                type TEXT,
                is_read BOOLEAN default false
    )""")
    db.close()


if __name__ == "__main__":
    create()
    input()