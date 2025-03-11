from db_client import cursor

def create():
    with open("tools/init_db/init-db.sql", 'r', encoding='utf-8') as file:
        sql_script = file.read()
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)

    print('Database initialized successfully!')


if __name__ == "__main__":
    create()