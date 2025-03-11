from app.trash.create_ldb import create_ldb
from sqlite3 import connect, IntegrityError
from .logs import elog


class Library:
    tables = ["available_books", "onhands_books", "backup_table", "autofill_table"]  # список таблиц
    fields = ("inventory_num", "title_ru", "title_original", "series",
              "lang_of_book", "lang_original", "author_ru", "author_in_original_lang",
              "writing_year", "transfer_year", "translators", "explanation_ru",
              "applications", "dimensions", "publication_year", "edition_num",
              "publishing_house", "isbn1", "isbn2", "abstract",
              "book_type", "book_genre", "cover_photo", "age_of_reader",
              "quantity", "location", "condition")

    onhands_fields = fields + ("name", "deadline")
    common_fields = ("title_ru", "title_original", "series",
              "lang_of_book", "lang_original", "author_ru", "author_in_original_lang",
              "writing_year", "transfer_year", "translators", "dimensions", "publication_year", "edition_num",
              "publishing_house", "isbn1", "isbn2", "abstract", "book_genre", "age_of_reader")
    int_fields = ("writing_year", "transfer_year", "publication_year",
                  "edition_num", "isbn1", "isbn2", "quantity")
    base_fields = ("inventory_num", "title_ru", "title_original", "author_ru", "author_in_original_lang", "book_genre")

    def __init__(self, path_to_db="db/library.db"):
        """
        Подключение к БД при
        инициализации. Аргумент
        path_to_db принимает путь к БД.
        По умолчанию равен "db/library.db".
        """
        self.path_to_db = path_to_db
        self.db = connect(self.path_to_db)
        self.db_curs = self.db.cursor()
        self.db.commit()
        # тест на наличие таблиц
        self.test_crashed = 0
        if self.test():
            self.test_crashed = 1

    def __all__(self):
        return ["add_book", "move_book", "delete_book", "edit_book", "get_m_rows_from_n"]

    def __del__(self):
        self.db_curs.close()
        self.db.close()

    def test(self):
        """
        Тест на наличие таблиц. Если их нет, то вызывается функция create_ldb.
        """
        try:
            self.db.execute("select inventory_num from available_books")
            self.db.execute("select inventory_num from onhands_books")
            self.db.execute("select inventory_num from backup_table")
            return 0
        except:
            r = create_ldb(self.path_to_db)
            if r:
                print(10 * "=" + "\nSame error with creating db or any table!\n" + "=" * 10)
                return 1

    def add_book(self,
                 inventory_num="",
                 title_ru="",
                 title_original="",
                 series="",
                 lang_of_book="",
                 lang_original="",
                 author_ru="",
                 author_in_original_lang="",
                 writing_year=0,
                 transfer_year=0,
                 translators="",
                 explanation_ru="",
                 applications="",
                 dimensions="",
                 publication_year=0,
                 edition_num=0,
                 publishing_house="",
                 isbn1=0,
                 isbn2=0,
                 abstract="",
                 book_type="",
                 book_genre="",
                 cover_photo="",
                 age_of_reader="",
                 quantity=0,
                 location="",
                 condition=""
                 ):
        """
		Добавление новой книги в таблицу "available_books". Принимаемые аргументы применяются в SQL-запросе "insert".
		Параметры:
			inventory_num - инвертарный номер, по умолчанию "";
			title_ru - название на русском, по умолчанию "";
			title_original - название оригинала, по умолчанию "";
			series - серия, по умолчанию "";
			lang_of_book - язык книги, по умолчанию "";
			lang_original - язык оригинала, по умолчанию "";
			author_ru - автор на русском, по умолчанию "";
			author_in_original_lang - автор на языке оригинала, по умолчанию "";
			writing_year - год написания, по умолчанию 0;
			transfer_year - год перевода, по умолчанию 0;
			translators - переводчики, по умолчанию "";
			explanation_ru - пояснение на русском, по умолчанию "";
			applications - приложения, по умолчанию "";
			dimensions - размеры, по умолчанию "";
			publication_year - год издания, по умолчанию 0;
			edition_num - номер издания, по умолчанию 0;
			publishing_house - издательство, по умолчанию "";
			isbn1 - ISBN 1, по умолчанию 0;
			isbn2 - ISBN 2, по умолчанию 0;
			abstract - аннотация, по умолчанию "";
			book_type - тип книги, по умолчанию "";
			book_genre - жанр книги, по умолчанию "";
			cover_photo - путь к фотографии обложки, по умолчанию "";
			age_of_reader - возраст читателя, по умолчанию "";
			quantity - количество, по умолчанию 0;
			location - место, по умолчанию "";
			condition - состояниепо умолчанию "".
		"""
        try:
            query = f"""
                insert into available_books {self.fields} values (
                    '{inventory_num}',
                    '{title_ru}',
                    '{title_original}',
                    '{series}',
                    '{lang_of_book}',
                    '{lang_original}',
                    '{author_ru}',
                    '{author_in_original_lang}',
                    {writing_year},
                    {transfer_year},
                    '{translators}',
                    '{explanation_ru}',
                    '{applications}',
                    '{dimensions}',
                    {publication_year},
                    {edition_num},
                    '{publishing_house}',
                    {isbn1},
                    {isbn2},
                    '{abstract}',
                    '{book_type}',
                    '{book_genre}',
                    '{cover_photo}',
                    '{age_of_reader}',
                    {quantity},
                    '{location}',
                    '{condition}'
                )
            """
            #print(query.replace('\n', ' ').replace("                    ", ""))
            self.db.execute(query)
            self.db.commit()
            return 0
        except IntegrityError as e:
            elog(e, file="library_control", line=118)
            return 1

    def move_book(self, from_tbl, to_tbl, inventory_num, name="", deadline=""):
        """
		Для переноса книг из таблицы  "from_tbl" в таблицу "to_tbl".
		Аргументы:
			from_tbl - название таблицы, из какой перенести, строка;
			to_tbl - название таблицы, в которую перенести, строка;
			inventory_number - инвертарный номер переносимой книги, строка.
	"""
        try:
            self.db_curs.execute(f"select * from {from_tbl} where inventory_num='{inventory_num}'")
            tmp = self.db_curs.fetchone()
            if tmp == None: return 2
            if to_tbl == self.tables[1]:
                tmp += (name, deadline)
            self.db_curs.execute(f"delete from {from_tbl} where inventory_num='{inventory_num}'")
            if to_tbl == self.tables[1]:
                self.db_curs.execute(f"insert into {to_tbl} {self.onhands_fields} values {tuple(tmp)}")
            if from_tbl == self.tables[1]:
                self.db_curs.execute(f"insert into {to_tbl} {self.fields} values {tuple(tmp)[:-2]}")
            self.db.commit()
            return 0
        except Exception as e:
            elog(e, file="library_control", line=166)
            return 1

    def delete_book(self, from_tbl, inventory_num):
        """
	    Перемещает книгу из таблицы from_tbl в резервную
	    таблицу.
	    Аргументы:
	    	from_tbl - название таблицы, из какой перенести, строка;
	    	inventory_number - инвертарный номер переносимой книги, строка.
	"""
        return self.move_book(from_tbl, "backup_table", inventory_num)

    def restore_book(self, inventory_num):
        """
	    Перемещает книгу из резервной таблицы в таблицу доступных книг.
	    Аргументы:
	    	inventory_number - инвертарный номер переносимой книги, строка.
	"""
        return self.move_book("backup_table", "available_books", inventory_num)

    def delete_book_from_deleted(self, inventory_num):
        """
	    Полностью удаляет книгу из базы данных.
	    Аргумент:
	    	inventory_number - инвертарный номер удаляемой книги, строка.
	"""
        try:
            self.db_curs.execute(f"delete from backup_table where inventory_num='{inventory_num}'")
            self.db.commit()
            return 0
        except Exception as e:
            elog(e, file="library_control", line=207)
            return 1

    def edit_book(self, table, inventory_num, fields_to_change: tuple, new_values: tuple):
        """
            Редактирует запись книги.
            Аргументы:
		table - название таблицы, в которой находится книга, строка;
    		inventory_number - инвертарный номер книги, строка;
	    	fields_to_change - поля, в которые вносятся изменения, кортёж;
		new_values - новые значения, кортёж.
        """
        try:
            names_values = ""
            if fields_to_change != () and new_values != ():
                n = len(new_values)
                for i in range(n):
                    names_values += fields_to_change[i] + "="
                    if fields_to_change[i] not in self.int_fields:
                        names_values += f"'{new_values[i]}'"
                    else:
                        names_values += str(new_values[i] if new_values[i] != "" else "0")
                    if i != n - 1:
                        names_values += ", "

            self.db.execute(f"update {table} set {names_values} where inventory_num='{inventory_num}'")
            self.db.commit()
            return 0
        except Exception as e:
            elog(e, file="library_control", line=224)
            return 1

    def get_m_rows_from_n(self, table, n, m, filter_=""):
        """
		Возвращает <= m книг из таблицы table начиная с (n-1)-ой книги.
		Добавлен фильтр. filter_ = "Field='Value'"  new "Field like '%Value%'"
		Аргументы:
			table - название таблицы, из которой достаются книги, строка;
			n - с какой книги по счёту, число;
			m - сколько книг, число.
			Может вернуть меньше m книг.
		"""
        try:
            self.db_curs.execute(f"select inventory_num, title_ru, title_original, author_ru, author_in_original_lang, book_genre from {table} {'' if filter_=='' else 'where '+filter_} order by title_ru limit {m} offset ({n - 1})")
            return self.db_curs.fetchall()
        except Exception as e:
            elog(e, file="library_control", line=258)
            return 1

    def get_one(self, table, inventory_num):
        try:
            self.db_curs.execute(f"select * from {table} where inventory_num={inventory_num}")
            return self.db_curs.fetchone()
        except Exception as e:
            elog(e, file="library_control", line=258)
            return 1

    def clear_autofill_table(self):
        try:
            self.db.execute("DROP TABLE IF EXISTS autofill_table")
            self.db.execute("""CREATE TABLE autofill_table (
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
                dimensions TEXT,
                publication_year INTEGER,
                edition_num INTEGER,
                publishing_house TEXT,
                isbn1 INTEGER,
                isbn2 INTEGER,
                abstract TEXT,
                book_genre TEXT,
                age_of_reader TEXT
            )""")

            self.db.commit()
            return 0
        except Exception as e:
            elog(e, file="library_control", line=261)
            return 1

    def add_to_autofill_table(self, values: list):
        values = list(values)
        try:
            if len(values) > 27:
                values = values[:-2]
            if len(values) > 19:
                for i in [26, 25, 24, 22, 20, 12, 11, 0]:
                    values.pop(i)
            self.db.execute(f"insert into autofill_table {self.common_fields} values {tuple(values)}")
            self.db.commit()
            return 0
        except Exception as e:
            elog(e, file="library_control", line=313)
            return 1

    def find_by_field_value(self, field, value, table=tables[0]):
        """
            Ищет записи, которые в заданном поле field содержат значение value.
            Возвращает список книг, если нашёл, иначе пустой список.
            Чтобы работало хорошо, value надо передавать с одинарными кавычками, если это строка, и без кавычек, если число.
            NEW. Хотя и числа можно передавать в кавычках, оказывается :о
        """
        try:
            self.db_curs.execute(f"select * from {table} where {field} like '%{value}%'")
            return self.db_curs.fetchall()
        except Exception as e:
            elog(e, file="library_control", line=311)
            return 1

    def get_places_list(self):
        """
             Возвращает список мест хранения книг
        """
        try:
            self.db_curs.execute(f"select distinct location from available_books")
            locations = []
            for i in self.db_curs.fetchall():
                locations += i

            locations.sort()
            if locations[0] == "":
                locations = locations[1:] + [locations[0]]
                
            return locations
        except Exception as e:
            elog(e, file="library_control", line=325)
            return 1
