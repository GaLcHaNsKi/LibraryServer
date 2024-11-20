from sqlite3 import connect
db = connect("company.db")

db.execute("create table if not exists client_passed (NO INTEGER primary key, id INTEGER, date STRING, number STRING)")
db.execute("create table if not exists client_rent (NO INTEGER primary key, name STRING, who STRING, number STRING, entrance STRING, exit STRING)")
db.execute("create table if not exists employee_ent (NO INTEGER primary key, name STRING, date STRING, time STRING)")
db.execute("create table if not exists employee_left (NO INTEGER primary key, name STRING, where_left STRING, time STRING)")
db.execute("create table if not exists users (ID INTEGER primary key, user STRING, password STRING, unique(user))")

db.commit()
db.close()

dbr = connect("company_recovery.db")

dbr.execute("create table if not exists client_passed (NO INTEGER primary key, id INTEGER, date STRING, number STRING)")
dbr.execute("create table if not exists client_rent (NO INTEGER primary key, name STRING, who STRING, number STRING, entrance STRING, exit STRING)")
dbr.execute("create table if not exists employee_ent (NO INTEGER primary key, name STRING, date STRING, time STRING)")
dbr.execute("create table if not exists employee_left (NO INTEGER primary key, name STRING, where_left STRING, time STRING)")
dbr.execute("create table if not exists users (ID INTEGER primary key, user STRING, password STRING, unique(user))")

dbr.commit()
dbr.close()