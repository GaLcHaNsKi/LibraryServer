from sqlite3 import connect
from app import DATABASE_PATH
from .logs import elog

DATABASE = DATABASE_PATH

def send_notify(author, recipient, title, content, type_):
    db = connect(DATABASE)
    code = 0
    try:
        db.execute(f"insert into notifications (author, recipient, title, content, type) values ('{author}', '{recipient}', '{title}', '{content}', '{type_}')")
        db.commit()
    except Exception as e:
        elog(e, file="notifications_control", line=9)
        code = 1
    db.close()
    return code

def del_notify(author, recipient, title, content):
    db = connect(DATABASE)
    code = 0
    try:
        db.execute(f"delete from notifications where author='{author}' and recipient='{recipient}' and title='{title}' and content='{content}'")
        db.commit()
    except Exception as e:
        elog(e, file="notifications_control", line=21)
        code = 1
    db.close()
    return code

def get_notify(recipient):
    db = connect(DATABASE)
    db_curs = db.cursor()
    code = 0
    ntfs = dict({})
    try:
        db_curs.execute(f"select * from notifications where recipient='{recipient}'")
        tmp = db_curs.fetchall()
        i = 1
        for n in tmp:
            ntfs[str(i)] = {"author": n[0], "recipient": n[1], "title": n[2], "text": n[3], "type": n[4]}
            i += 1
    except Exception as e:
        elog(e, file="notifications_control", line=35)
        code = 1
    db.close()
    return ntfs if code == 0 else 1

def have_notify(recipient):
    db = connect(DATABASE)
    db_curs = db.cursor()
    code = 0
    tmp = []
    try:
        db_curs.execute(f"select * from notifications where recipient='{recipient}' and is_read=0")
        tmp = db_curs.fetchall()
        db.execute(f"update notifications set is_read=true where recipient='{recipient}'")
        db.commit()
    except Exception as e:
        elog(e, file="notifications_control", line=53)
        code = 1
    return (tmp != []) if code == 0 else -1