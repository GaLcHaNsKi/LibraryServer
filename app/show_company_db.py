from sqlite3 import connect
db = connect("company.db")
db_curs = db.cursor()

db_curs.execute("select * from client_rent")
print("\nTable: client_rent")
ft = db_curs.fetchall()
for i in ft:
    print(i)

db_curs.execute("select * from employee_ent")
print("\nTable: employee_ent")
ft = db_curs.fetchall()
for i in ft:
    print(i)

db_curs.execute("select * from employee_left")
print("\nTable: employee_left")
ft = db_curs.fetchall()
for i in ft:
    print(i)

db_curs.execute("select * from client_passed")
print("\nTable: client_passed")
ft = db_curs.fetchall()
for i in ft:
    print(i)
db.close()