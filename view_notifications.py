from sqlite3 import connect

db = connect("app.db")
db_curs = db.cursor()
db_curs.execute("select * from notifications")

#db.execute("insert into notifications (author, recipient, title, content, type) values ('Library', 'Q', 'Welcome1', 'Hello, Q!', 'send')")
db.commit()
notifications = db_curs.fetchall()
for i in notifications:
    print(i)

if __name__ == "__main__": input()
