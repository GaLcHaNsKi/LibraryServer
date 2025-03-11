from sqlite3 import connect

db = connect("../../app.db")
db_curs = db.cursor()
db_curs.execute("select * from notifications")#("drop table notifications")
notifications = db_curs.fetchall()
for i in notifications:
    print(i)

if __name__ == "__main__": input()