import pymysql

connection = pymysql.connect(
    host='localhost',
    user='worker',
    password='worker',
    database='library'
)
print("Database connected!")

connection.autocommit(True)

cursor = connection.cursor()
