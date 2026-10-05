from app import db
from app.models import BookGenre, DocumentType, BookCondition, BibleBook, Library
from sqlalchemy import inspect
from app.views.logs import elog


def _upsert_genres():
    genres_ru = [
    "Автобиография",
    "Абсурдная драма",
    "Антироман",
    "Баллада",
    "Басня",
    "Биография",
    "Водевиль",
    "Героическая поэма",
    "Героическое фэнтези",
    "Городское фэнтези",
    "Детектив",
    "Детская литература",
    "Драма",
    "Журнал",
    "Зарубежная классика",
    "Зарубежная роман",
    "Зарубежные остросюжетные",
    "Зарубежные приключения",
    "Зарубежная юмор",
    "Зарубежная история",
    "Зарубежная фантастика",
    "Зарубежные детективы",
    "Зарубежная проза",
    "Зарубежная поэзия",
    "Искусство",
    "Исторический роман",
    "История",
    "Кулинария",
    "Лирическая поэма",
    "Лирическое стихотворение",
    "Мадригал",
    "Мелодрама",
    "Мемуары",
    "Наука",
    "Новелла",
    "Нуар",
    "Ода",
    "Очерк",
    "Послание",
    "Поэма",
    "Поэзия",
    "Приключения",
    "Притча",
    "Псалом",
    "Публицистика",
    "Путешествия",
    "Пьеса",
    "Психология",
    "Рассказ",
    "Религия",
    "Роман",
    "Сатира",
    "Сатирическая комедия",
    "Сонет",
    "Справочник",
    "Стансы",
    "Трагедия",
    "Трагикомедия",
    "Трактат",
    "Учебник",
    "Фабула",
    "Фарс",
    "Фантастика",
    "Фэнтези",
    "Философия",
    "Философская поэма",
    "Элегия",
    "Эпическая поэма",
    "Эпиграмма",
    "Эпитала",
    "Эпопея",
    "Эссе",
    "Эпитафия"
]

    existing = {g.genre_name for g in BookGenre.query.all()}
    for name in genres_ru:
        if name not in existing:
            db.session.add(BookGenre(genre_name=name, description=""))


def _upsert_document_types():
    doc_types_ru = [
        "Книга", "Журнал", "Газета", "Брошюра", "Рукопись",
        "Электронный ресурс", "Сборник", "Альбом", "Справочник", "Учебник"
    ]

    existing = {t.type_name for t in DocumentType.query.all()}
    for name in doc_types_ru:
        if name not in existing:
            db.session.add(DocumentType(type_name=name, description=""))


def _upsert_default_conditions():
    default_conditions = ["Отличное", "Хорошее", "Удовлетворительное", "Плохое"]

    existing = {c.condition_name for c in BookCondition.query.all()}
    for name in default_conditions:
        if name not in existing:
            db.session.add(BookCondition(condition_name=name))


def _upsert_bible_books():
    # Полный список 66 книг Библии в используемом в приложении порядке.
    # Английское название служит постоянным ключом: русские названия и сокращения
    # можно безопасно исправлять без изменения ссылок книг на BibleBook.
    books = [
        ("Бытие", "Genesis", "Быт"), ("Исход", "Exodus", "Исх"), ("Левит", "Leviticus", "Лев"), ("Числа", "Numbers", "Чис"),
        ("Второзаконие", "Deuteronomy", "Втор"), ("Иисуса Навина", "Joshua", "Нав"), ("Судьи", "Judges", "Суд"), ("Руфь", "Ruth", "Руф"),
        ("1 Царств", "1 Samuel", "1 Цар"), ("2 Царств", "2 Samuel", "2 Цар"), ("3 Царств", "1 Kings", "3 Цар"), ("4 Царств", "2 Kings", "4 Цар"),
        ("1 Паралипоменон", "1 Chronicles", "1 Пар"), ("2 Паралипоменон", "2 Chronicles", "2 Пар"), ("Ездра", "Ezra", "Езд"),
        ("Неемия", "Nehemiah", "Неем"), ("Есфирь", "Esther", "Есф"), ("Иов", "Job", "Иов"), ("Псалтирь", "Psalms", "Пс"),
        ("Притчи", "Proverbs", "Прит"), ("Екклесиаст", "Ecclesiastes", "Еккл"), ("Песни песней", "Song of Solomon", "Песн"),
        ("Исаия", "Isaiah", "Ис"), ("Иеремия", "Jeremiah", "Иер"), ("Плач Иеремии", "Lamentations", "Плач"), ("Иезекииль", "Ezekiel", "Иез"),
        ("Даниил", "Daniel", "Дан"), ("Осия", "Hosea", "Ос"), ("Иоиль", "Joel", "Иоил"), ("Амос", "Amos", "Ам"), ("Авдий", "Obadiah", "Авд"),
        ("Иона", "Jonah", "Ион"), ("Михей", "Micah", "Мих"), ("Наум", "Nahum", "Наум"), ("Аввакум", "Habakkuk", "Авв"), ("Софония", "Zephaniah", "Соф"),
        ("Аггей", "Haggai", "Агг"), ("Захария", "Zechariah", "Зах"), ("Малахия", "Malachi", "Мал"),
        ("Матфея", "Matthew", "Мф"), ("Марка", "Mark", "Мк"), ("Луки", "Luke", "Лк"), ("Иоанна", "John", "Ин"),
        ("Деяния", "Acts", "Деян"), ("Иакова", "James", "Иак"), ("1 Петра", "1 Peter", "1 Пет"), ("2 Петра", "2 Peter", "2 Пет"),
        ("1 Иоанна", "1 John", "1 Ин"), ("2 Иоанна", "2 John", "2 Ин"), ("3 Иоанна", "3 John", "3 Ин"), ("Иуды", "Jude", "Иуд"),
        ("Римлянам", "Romans", "Рим"), ("1 Коринфянам", "1 Corinthians", "1 Кор"), ("2 Коринфянам", "2 Corinthians", "2 Кор"),
        ("Галатам", "Galatians", "Гал"), ("Ефесянам", "Ephesians", "Еф"), ("Филиппийцам", "Philippians", "Флп"), ("Колоссянам", "Colossians", "Кол"),
        ("1 Фессалоникийцам", "1 Thessalonians", "1 Фес"), ("2 Фессалоникийцам", "2 Thessalonians", "2 Фес"),
        ("1 Тимофею", "1 Timothy", "1 Тим"), ("2 Тимофею", "2 Timothy", "2 Тим"), ("Титу", "Titus", "Тит"),
        ("Филимону", "Philemon", "Флм"), ("Евреям", "Hebrews", "Евр"), ("Откровение", "Revelation", "Откр")
    ]

    # ``flask db upgrade`` imports the application before the migration is
    # applied. Do not select the new columns until that migration exists.
    columns = {column["name"] for column in inspect(db.engine).get_columns("bible_books")}
    if not {"abbreviation", "sort_order"}.issubset(columns):
        return

    existing_by_en = {b.en: b for b in BibleBook.query.all()}
    for sort_order, (ru, en, abbreviation) in enumerate(books, start=1):
        book = existing_by_en.get(en)
        if book is None:
            db.session.add(BibleBook(
                ru=ru,
                en=en,
                abbreviation=abbreviation,
                sort_order=sort_order,
            ))
        else:
            book.ru = ru
            book.abbreviation = abbreviation
            book.sort_order = sort_order


def fillReferenceTables():
    """
    Заполняет справочники: жанры, типы документов, состояния книг (по библиотекам) и книги Библии.
    Названия на русском языке.
    Вызывать один раз при инициализации БД. Повторные вызовы идемпотентны.
    """
    try:
        _upsert_genres()
        _upsert_document_types()
        _upsert_default_conditions()
        _upsert_bible_books()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        elog(e, file="fill_reference_tables", function="fillReferenceTables")
        raise
