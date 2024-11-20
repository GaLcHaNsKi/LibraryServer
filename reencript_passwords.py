import hashlib
from sqlite3 import connect

def hash_password(password):
    # Преобразуем строку в байты
    password_bytes = password.encode('utf-8')
    
    # Создаем объект хеширования
    hash_object = hashlib.sha256(password_bytes)
    
    # Получаем хеш в шестнадцатеричном формате
    hex_dig = hash_object.hexdigest()
    
    return hex_dig

db = connect("./app.db")
db_curs = db.cursor()

db_curs.execute("select * from users")

users = db_curs.fetchall()

for user in users:
    db.execute(f"update users set coded_password='{hash_password(user[2])}' where id={user[0]}")

db.commit()
db.close()
