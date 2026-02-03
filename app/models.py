from . import db

from sqlalchemy import Enum, CheckConstraint
import enum


class Role(enum.Enum):
    OWNER = "OWNER"
    LIBRARIAN = "LIBRARIAN"
    READER = "READER"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(35), unique=True)
    password_hash = db.Column(db.Text)
    role = db.Column(Enum(Role))


class Library(db.Model):
    __tablename__ = 'libraries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    director_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))


class Librarian(db.Model):
    __tablename__ = 'librarians'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    is_hired = db.Column(db.Boolean, default=False)
    director_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="SET NULL"))


class Director(db.Model):
    __tablename__ = 'directors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="SET NULL"))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    title = db.Column(db.String(25))
    content = db.Column(db.Text)
    type = db.Column(db.String(10))
    is_read = db.Column(db.Boolean, default=False)


class BookGenre(db.Model):
    __tablename__ = 'book_genres'
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)


class DocumentType(db.Model):
    __tablename__ = 'document_types'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)


class BookCondition(db.Model):
    __tablename__ = 'book_conditions'
    id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.String(50))
    __table_args__ = (db.UniqueConstraint('condition_name'),)


class Place(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="CASCADE"))
    place_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint('library_id', 'place_name'),)


class Shelf(db.Model):
    __tablename__ = 'shelves'
    id = db.Column(db.Integer, primary_key=True)
    shelve_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete="CASCADE"))
    __table_args__ = (db.UniqueConstraint('place_id', 'shelve_name'),)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="CASCADE"), nullable=False)
    is_on_hand = db.Column(db.Boolean, default=False)
    inventory_num = db.Column(db.String(50), nullable=False)
    title_ru = db.Column(db.Text)
    title_original = db.Column(db.Text)
    series = db.Column(db.Text)
    lang_of_book = db.Column(db.String(50))
    lang_original = db.Column(db.String(50))
    author_ru = db.Column(db.String(20))
    author_in_original_lang = db.Column(db.String(20))
    writing_year = db.Column(db.Integer)
    transfer_year = db.Column(db.Integer)
    translators = db.Column(db.Text)
    explanation_ru = db.Column(db.Text)
    applications = db.Column(db.Text)
    dimensions = db.Column(db.String(50))
    publication_year = db.Column(db.Integer)
    edition_num = db.Column(db.Integer)
    publishing_house = db.Column(db.String(50))
    isbn1 = db.Column(db.String(13))  # можно добавить валидацию вручную
    isbn2 = db.Column(db.String(13))
    abstract = db.Column(db.Text)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id', ondelete="SET NULL"))
    book_genre_id = db.Column(db.Integer, db.ForeignKey('book_genres.id', ondelete="SET NULL"))
    book_genre = db.relationship("BookGenre", backref="books")
    cover_photo_uuid = db.Column(db.String(40))
    age_of_reader = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('places.id', ondelete="CASCADE"), nullable=False)
    shelve_id = db.Column(db.Integer, db.ForeignKey('shelves.id', ondelete="CASCADE"), nullable=False)
    condition_id = db.Column(db.Integer, db.ForeignKey('book_conditions.id', ondelete="SET NULL"))
    pages_quantity = db.Column(db.Integer)
    keywords = db.relationship("Keyword", backref="book", cascade="all, delete-orphan")
    bible_places = db.relationship(
        "BiblePlaceInBook",
        backref="book",
        cascade="all, delete-orphan"
    )
    topics_links = db.relationship(
        "BookTopic",
        backref="book",
        cascade="all, delete-orphan"
    )
    # Relationships for convenience used across services
    document_type = db.relationship("DocumentType", backref="books", foreign_keys=[document_type_id])
    location = db.relationship("Place", backref="books", foreign_keys=[location_id])
    shelve = db.relationship("Shelf", backref="books", foreign_keys=[shelve_id])
    condition = db.relationship("BookCondition", backref="books", foreign_keys=[condition_id])
    __table_args__ = (
        db.UniqueConstraint('library_id', 'inventory_num'),
        CheckConstraint('transfer_year > 1000'),
        CheckConstraint('quantity >= 0'),
        CheckConstraint('pages_quantity > 0'),
    )


class OnHandsBook(db.Model):
    __tablename__ = 'on_hands_books'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="CASCADE"))
    recipient_name = db.Column(db.String(20))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    issue_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    __table_args__ = (CheckConstraint('issue_date <= return_date'),)


class NotificationSetting(db.Model):
    __tablename__ = 'notification_settings'
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id', ondelete="CASCADE"))
    notify_before_days = db.Column(db.Integer, default=1)
    notify_after_days = db.Column(db.Integer, default=0)
    is_every_day = db.Column(db.Boolean)


class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="CASCADE"))
    pages = db.Column(db.Text)


class BookTopic(db.Model):
    __tablename__ = 'books_topics'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="CASCADE"))
    topic_name = db.Column(db.String(15), nullable=False)
    pages = db.Column(db.Text)


class BibleBook(db.Model):
    __tablename__ = 'bible_books'
    id = db.Column(db.Integer, primary_key=True)
    ru = db.Column(db.String(30))
    en = db.Column(db.String(30))


class BiblePlaceInBook(db.Model):
    __tablename__ = 'bible_place_in_book'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete="CASCADE"))
    bible_book_id = db.Column(db.Integer, db.ForeignKey('bible_books.id', ondelete="CASCADE"))
    chapter = db.Column(db.Integer)
    verse = db.Column(db.Integer)
    pages = db.Column(db.Text)
    bible_book = db.relationship("BibleBook", backref="bible_places")
