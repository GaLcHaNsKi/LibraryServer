from sqlite3 import connect
def clear_all(path="company.db"):
    db = connect(path)
    db.execute("delete from client_rent")
    db.execute("delete from employee_ent")
    db.execute("delete from employee_left")
    db.execute("delete from client_passed")
    db.commit()
    db.close()

if __name__ == "__main__":
    clear_all()