from sqlite3 import connect
def create_ldb(path_to_db="./db/library.db"):
	"""
	Создание БД, при отсутствии, и таблиц:
		available_books - доступные книги;
		onhands_books - книги, которые "на руках;
		backup_table - резервная таблица.
	Параметр:
		path_to_db - путь к БД.
	Возвращает:
		0, если таблицы созданы;
		1, если хоть одна не создана.
	"""
	db = connect(path_to_db)
	db.execute("""CREATE TABLE available_books (
		inventory_num TEXT PRIMARY KEY,
		title_ru TEXT,
		title_original TEXT,
		series TEXT,
		lang_of_book TEXT,
		lang_original TEXT,
		author_ru TEXT,
		author_in_original_lang TEXT,
		writing_year INTEGER,
		transfer_year INTEGER,
		translators TEXT,
		explanation_ru TEXT,
		applications TEXT,
		dimensions TEXT,
		publication_year INTEGER,
		edition_num INTEGER,
		publishing_house TEXT,
		isbn1 INTEGER,
		isbn2 INTEGER,
		abstract TEXT,
		book_type TEXT,
		book_genre TEXT,
		cover_photo TEXT,
		age_of_reader TEXT,
		quantity INTEGER,
		location TEXT,
		condition TEXT
	)""")
	db.execute("""CREATE TABLE onhands_books (
		inventory_num TEXT PRIMARY KEY,
		title_ru TEXT,
		title_original TEXT,
		series TEXT,
		lang_of_book TEXT,
		lang_original TEXT,
		author_ru TEXT,
		author_in_original_lang TEXT,
		writing_year INTEGER,
		transfer_year INTEGER,
		translators TEXT,
		explanation_ru TEXT,
		applications TEXT,
		dimensions TEXT,
		publication_year INTEGER,
		edition_num INTEGER,
		publishing_house TEXT,
		isbn1 INTEGER,
		isbn2 INTEGER,
		abstract TEXT,
		book_type TEXT,
		book_genre TEXT,
		cover_photo TEXT,
		age_of_reader TEXT,
		quantity INTEGER,
		location TEXT,
		condition TEXT
	)""")
	db.execute("""CREATE TABLE backup_table (
		inventory_num TEXT,
		title_ru TEXT,
		title_original TEXT,
		series TEXT,
		lang_of_book TEXT,
		lang_original TEXT,
		author_ru TEXT,
		author_in_original_lang TEXT,
		writing_year INTEGER,
		transfer_year INTEGER,
		translators TEXT,
		explanation_ru TEXT,
		applications TEXT,
		dimensions TEXT,
		publication_year INTEGER,
		edition_num INTEGER,
		publishing_house TEXT,
		isbn1 INTEGER,
		isbn2 INTEGER,
		abstract TEXT,
		book_type TEXT,
		book_genre TEXT,
		cover_photo TEXT,
		age_of_reader TEXT,
		quantity INTEGER,
		location TEXT,
		condition TEXT
	)""")
	try: # проверка на существование таблиц
		db.execute("select * from available_books")
		db.execute("select * from onhands_books")
		db.execute("select * from backup_table")
		db.close()
		return 0
	except:
		db.close()
		return 1
