from sqlite3 import connect
from sys import argv
from encoder import encode, table

user = str(argv[1])
password = str(argv[2])
retry_password = str(argv[3])

for l in password:
    is_in = 0
    for row in table:
        if l in row:
            is_in = 1
            break
    if not is_in:
        print("Illegal character: "+l)
        exit()

if password != retry_password:
    print("Passwords is not equals!")
    exit()

print(encode(password))
encoded_password = encode(password)[0]
db = connect("/home/Galchanskiy/Library/app/company.db")
db.execute(f"insert into users (user, password) values ('{user}', '{encoded_password}')")
db.commit()
db.close()