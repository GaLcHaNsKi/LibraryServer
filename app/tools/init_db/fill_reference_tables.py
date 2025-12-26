from app import db
from app.models import BookGenre, DocumentType, BookCondition, BibleBook, Library
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
    # Полный список 66 книг Библии (русские и английские названия)
    books = [
        ("Бытие", "Genesis"), ("Исход", "Exodus"), ("Левит", "Leviticus"), ("Числа", "Numbers"),
        ("Второзаконие", "Deuteronomy"), ("Иисус Навин", "Joshua"), ("Судьи", "Judges"), ("Руфь", "Ruth"),
        ("1 Царств", "1 Samuel"), ("2 Царств", "2 Samuel"), ("3 Царств", "1 Kings"), ("4 Царств", "2 Kings"),
        ("1 Паралипоменон", "1 Chronicles"), ("2 Паралипоменон", "2 Chronicles"), ("Ездра", "Ezra"),
        ("Неемия", "Nehemiah"), ("Есфирь", "Esther"), ("Иов", "Job"), ("Псалтирь", "Psalms"),
        ("Притчи", "Proverbs"), ("Экклезиаст", "Ecclesiastes"), ("Песня песней", "Song of Solomon"),
        ("Исаия", "Isaiah"), ("Иеремия", "Jeremiah"), ("Плач Иеремии", "Lamentations"), ("Иезекииль", "Ezekiel"),
        ("Даниил", "Daniel"), ("Осия", "Hosea"), ("Иоиль", "Joel"), ("Амос", "Amos"), ("Авдий", "Obadiah"),
        ("Иона", "Jonah"), ("Михей", "Micah"), ("Наум", "Nahum"), ("Аввакум", "Habakkuk"), ("Софония", "Zephaniah"),
        ("Аггей", "Haggai"), ("Захария", "Zechariah"), ("Малахия", "Malachi"),
        ("Матфей", "Matthew"), ("Марк", "Mark"), ("Лука", "Luke"), ("Иоанн", "John"),
        ("Деяния", "Acts"), ("Римлянам", "Romans"), ("1 Коринфянам", "1 Corinthians"), ("2 Коринфянам", "2 Corinthians"),
        ("Галатам", "Galatians"), ("Ефесянам", "Ephesians"), ("Филиппийцам", "Philippians"), ("Колоссянам", "Colossians"),
        ("1 Фессалоникийцам", "1 Thessalonians"), ("2 Фессалоникийцам", "2 Thessalonians"), ("1 Тимофею", "1 Timothy"), ("2 Тимофею", "2 Timothy"),
        ("Титу", "Titus"), ("Филимону", "Philemon"), ("Евреям", "Hebrews"), ("Иаков", "James"),
        ("1 Петра", "1 Peter"), ("2 Петра", "2 Peter"), ("1 Иоанна", "1 John"), ("2 Иоанна", "2 John"), ("3 Иоанна", "3 John"),
        ("Иуда", "Jude"), ("Откровение", "Revelation")
    ]

    # Avoid duplicates by comparing RU names
    existing_ru = {b.ru for b in BibleBook.query.all()}
    for ru, en in books:
        if ru not in existing_ru:
            db.session.add(BibleBook(ru=ru, en=en))


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