from sqlite3 import connect
from sys import argv
db = connect("company.db")
table = str(argv[1])
db.execute(f"delete from {table}")
db.commit()
db.close()