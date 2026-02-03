import json

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import joinedload

from app.views.common_service import isExists
from app.views.logs import elog
from app import db
from app.models import Library, Book, Keyword, BookTopic, BiblePlaceInBook, OnHandsBook, BookGenre, BibleBook, \
    BookCondition, DocumentType, Place, Shelf


class LibraryClient:
    def addBook(self,
                 libraryId,
                 inventory_num,
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
                 document_type_id=None,
                 book_genre_id=None,
                 cover_photo_uuid=None,
                 age_of_reader="",
                 quantity=0,
                 location_id=None,
                 shelve_id=None,
                 condition_id=None,
                 pages_quantity=1,
                 keywords=None,  # [{"keyword": "keyword1", "pages": "pages1"}, ...]
                 topics=None,  # [{"topicId": "topic1_id", "pages": "pages1"}, ...]
                 bible_references=None  # [{"bibleBooId": "bible_book_id", "chapter": n, "verse": n, "pages": "pages1"}]
                 ):
        try:
            # Find library by name
            library_record = Library.query.filter_by(id=libraryId).first()
            if not library_record:
                return 1  # Library not found

            # Create new book
            new_book = Book(
                library_id=library_record.id,
                inventory_num=inventory_num,
                title_ru=title_ru,
                title_original=title_original,
                series=series,
                lang_of_book=lang_of_book,
                lang_original=lang_original,
                author_ru=author_ru,
                author_in_original_lang=author_in_original_lang,
                writing_year=writing_year,
                transfer_year=transfer_year,
                translators=translators,
                explanation_ru=explanation_ru,
                applications=applications,
                dimensions=dimensions,
                publication_year=publication_year,
                edition_num=edition_num,
                publishing_house=publishing_house,
                isbn1=isbn1,
                isbn2=isbn2,
                abstract=abstract,
                document_type_id=document_type_id,
                book_genre_id=book_genre_id,
                cover_photo_uuid=cover_photo_uuid,
                age_of_reader=age_of_reader,
                quantity=quantity,
                location_id=location_id,
                shelve_id=shelve_id,
                condition_id=condition_id,
                pages_quantity=pages_quantity
            )
            db.session.add(new_book)
            db.session.flush()  # Ensure book.id is available for related records

            # Insert keywords
            if keywords:
                keywords = json.load(keywords)
                for kw in keywords:
                    keyword = Keyword(keyword=kw.keyword, book_id=new_book.id, pages=kw.pages)
                    db.session.add(keyword)

            # Insert topics
            if topics:
                topics = json.load(topics)
                for topic in topics:
                    book_topic = BookTopic(book_id=new_book.id, topic_id=topic.topicId, pages=topic.pages)
                    db.session.add(book_topic)

            # Insert Bible references
            if bible_references:
                bible_references = json.load(bible_references)
                for bibleRef in bible_references:
                    bible_ref = BiblePlaceInBook(
                        book_id=new_book.id,
                        bible_book_id=bibleRef.bibleBookId,
                        chapter=bibleRef.chapter,
                        verse=bibleRef.verse,
                        pages=bibleRef.pages
                    )
                    db.session.add(bible_ref)

            # Commit all changes
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()  # Roll back on error
            elog(e, file="book_service", function="addBook")
            return 1

    def issueBook(self, bookId, recipient_name, deadline):
        try:
            # Get recipient_id
            recipient_id = isExists(recipient_name)

            # Get book_id (assumes get_book_id is a method in the same class)
            book = Book.query(Book.id).filter_by(id=bookId).first()
            if not book:
                return -1

            # Create OnHandsBook record
            on_hands_book = OnHandsBook(
                book_id=book.id,
                recipient_name=recipient_name,
                recipient_id=recipient_id or None,  # Convert 0 to None for nullable field
                return_date=deadline
            )
            db.session.add(on_hands_book)

            # Update book to set is_on_hand=True
            book.is_on_hand = True

            # Commit changes
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()  # Roll back on error
            elog(e, "book_service", "issueBook")
            return 1

    def returnBook(self, bookId) -> int:
        """
        Возвращает книгу: обновляет is_on_hand = False и удаляет все записи о выдаче.
        """
        try:
            # Получение ID книги
            book = Book.query(Book.id).filter_by(id=bookId).first()
            if not book:
                return -1

            # Удаление записей из OnHandsBook
            OnHandsBook.query.filter_by(book_id=book.id).delete()

            # Обновление флага is_on_hand
            book.is_on_hand = False

            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "returnBook")
            return 1

    def getBookId(self, library, inventory_num):
        try:
            # Find library by name
            library_record = Library.query.filter_by(name=library).first()
            if not library_record:
                return -1  # Library not found

            # Find book by inventory_num and library_id
            book = Book.query.filter_by(inventory_num=inventory_num, library_id=library_record.id).first()
            if not book:
                return -2  # Book not found

            return book.id

        except Exception as e:
            elog(e, "book_service", "getBookId")
            return 0

    def deleteBook(self, bookId: int) -> int:
        """
        Удаляет книгу по ID.
        Args:
            bookId (int): ID книги
        Returns:
            int: 0 — успех, 1 — ошибка, -1 - книга не найдена
        """
        try:
            book = Book.query.get(bookId)
            if not book:
                return -1  # Книга не найдена

            db.session.delete(book)
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "deleteBook")
            return 1

    def editBook(self, bookId: int, changes: dict):
        """
        Updates a book's fields.
        Args:
            bookId (int): ID книги
            changes: Data to change.
        """
        try:
            book = Book.query.filter_by(id=bookId).first()
            if not book:
                return -1  # Book not found

            # Update book fields
            for field, value in changes.items():
                if field in self.fields:
                    setattr(book, field, value)
                elif field == "topics":
                    self._updateTopics(book, value)
                elif field == "keywords":
                    self._updateKeywords(book, value)
                elif field == "bibleReferences":
                    self._updateBibleReferences(book, value)

            # Commit changes
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()  # Roll back on error
            elog(e, "book_service", "editBook")
            return 1

    def _updateTopics(self, book: Book, value: list[dict]):
        """
        Обновляет, добавляет и удаляет записи BookTopic для книги.

        Args:
            book (Book): Объект книги.
            value (list[dict]): Список словарей с темами. Формат:
                {
                    id: int | None  # ID записи в books_topics (не id темы!)
                    topic_id: int
                    pages: str
                }
        """
        try:
            # Получаем текущие связи книги с темами
            existing_links = {bt.id: bt for bt in book.topics_links}
            incoming_ids = set()

            for item in value:
                link_id = item.get("id")
                incoming_ids.add(link_id)

                if link_id is None:
                    # Новая связь
                    new_link = BookTopic(
                        book_id=book.id,
                        topic_id=item["topic_id"],
                        pages=item.get("pages", "")
                    )
                    db.session.add(new_link)
                elif link_id in existing_links:
                    # Обновление существующей связи
                    link = existing_links[link_id]
                    link.topic_id = item["topic_id"]
                    link.pages = item.get("pages", "")

            # Удаление неиспользуемых связей
            for link_id, link in existing_links.items():
                if link_id not in incoming_ids:
                    db.session.delete(link)

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "_updateTopics")
            raise e

    def _updateKeywords(self, book: Book, value: list[dict]):
        """
        Обновляет ключевые слова книги.
        value = [{
            "id": int | None,
            "keyword": str,
            "pages": str
        }]
        """
        try:
            existing_keywords = {kw.id: kw for kw in book.keywords}

            # IDs, которые остались актуальны
            updated_ids = set()

            for item in value:
                kw_id = item.get("id")
                kw_text = item.get("keyword")
                kw_pages = item.get("pages")

                if kw_id is None:
                    # Создание нового ключевого слова
                    new_kw = Keyword(keyword=kw_text, pages=kw_pages, book=book)
                    db.session.add(new_kw)
                elif kw_id in existing_keywords:
                    # Обновление существующего ключевого слова
                    kw = existing_keywords[kw_id]
                    kw.keyword = kw_text
                    kw.pages = kw_pages
                    updated_ids.add(kw_id)

            # Удаление ключевых слов, которые не переданы в новом списке
            for kw_id, kw_obj in existing_keywords.items():
                if kw_id not in updated_ids:
                    db.session.delete(kw_obj)

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "_updateKeywords")
            raise e

    def _updateBibleReferences(self, book: Book, value: list[dict]):
        """
        Обновляет, добавляет и удаляет записи BiblePlaceInBook для книги.

        Args:
            book (Book): Книга, для которой обновляются ссылки.
            value (list[dict]): Список словарей со ссылками. Формат:
                {
                    id: int | None
                    bibleBookId: int
                    chapter: int
                    verse: int
                    pages: str
                }
        """
        try:
            # Получаем все текущие записи
            existing_refs = {ref.id: ref for ref in book.bible_places}
            incoming_ids = set()

            for item in value:
                ref_id = item.get("id")
                incoming_ids.add(ref_id)

                if ref_id is None:
                    # Новая ссылка
                    new_ref = BiblePlaceInBook(
                        book_id=book.id,
                        bible_book_id=item["bibleBookId"],
                        chapter=item["chapter"],
                        verse=item["verse"],
                        pages=item.get("pages", "")
                    )
                    db.session.add(new_ref)
                elif ref_id in existing_refs:
                    # Обновление существующей записи
                    ref = existing_refs[ref_id]
                    ref.bible_book_id = item["bibleBookId"]
                    ref.chapter = item["chapter"]
                    ref.verse = item["verse"]
                    ref.pages = item.get("pages", "")
                else:
                    # ID есть, но не найдено в базе (возможна ошибка)
                    continue

            # Удаляем ссылки, которых нет в value
            for ref_id, ref in existing_refs.items():
                if ref_id not in incoming_ids:
                    db.session.delete(ref)

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "_updateBibleReferences")
            raise e

    def getBooks(self, libraryId: int | None, page: int = 1, take: int = 10, filters_: dict = None) -> dict | int:
        try:
            query = Book.query

            if libraryId:   # если указана библиотека, то ищем в ней
                query = Book.query.filter_by(library_id=libraryId)

            # Apply filters
            if filters_:
                for key, value in filters_.items():
                    if key == "topic":
                        query = query.outerjoin(Book.topics_links).filter(
                            BookTopic.topic_name.ilike(f"%{value}%"))
                    elif key == "genre":
                        query = query.outerjoin(Book.book_genre).filter(BookGenre.genre_name.ilike(f"%{value}%"))
                    elif key == "keyword":
                        query = query.outerjoin(Book.keywords).filter(Keyword.keyword.ilike(f"%{value}%"))
                    elif key == "bible":
                        query = query.outerjoin(Book.bible_places).outerjoin(BiblePlaceInBook.bible_book).filter(
                            BibleBook.ru.ilike(f"%{value}%"))
                    elif key == "location":
                        try:
                            location_id = int(value)
                            query = query.filter(Book.location_id == location_id)
                        except (ValueError, TypeError):
                            query = query.outerjoin(Book.location).filter(Place.place_name.ilike(f"%{value}%"))
                    elif key == "shelve":
                        try:
                            shelve_id = int(value)
                            query = query.filter(Book.shelve_id == shelve_id)
                        except (ValueError, TypeError):
                            query = query.outerjoin(Book.shelve).filter(Shelf.shelve_name.ilike(f"%{value}%"))
                    elif key == "condition":
                        query = query.outerjoin(Book.condition).filter(BookCondition.condition_name.ilike(f"%{value}%"))
                    elif key == "document_type":
                        query = query.outerjoin(Book.document_type).filter(DocumentType.type_name.ilike(f"%{value}%"))
                    elif hasattr(Book, key):
                        column = getattr(Book, key)
                        try:
                            col_type = getattr(Book.__table__.columns, key).type
                        except KeyError:
                            continue

                        if isinstance(col_type, String):
                            query = query.filter(column.ilike(f"%{value}%"))
                        elif isinstance(col_type, Boolean):
                            bool_value = str(value).lower() in ["true", "1", "yes"]
                            query = query.filter(column.is_(bool_value))
                        elif isinstance(col_type, Integer):
                            try:
                                query = query.filter(column == int(value))
                            except ValueError:
                                return 1  # Некорректный тип
                        else:
                            return 1  # Неподдерживаемый тип фильтра

            total = query.count()
            offset = page * take
            
            # Eager load relationships to avoid lazy loading issues
            query = query.options(
                joinedload(Book.book_genre),
                joinedload(Book.location),
                joinedload(Book.shelve),
                joinedload(Book.condition),
                joinedload(Book.document_type)
            )
            
            books = query.order_by(Book.title_ru).offset(offset).limit(take).all()

            return {
                "pages": (total + take - 1) // take,
                "data": [
                    {
                        "id": book.id,
                        "inventory_num": book.inventory_num,
                        "title_ru": book.title_ru,
                        "title_original": book.title_original,
                        "genre": book.book_genre.genre_name if book.book_genre else None,
                        "author_ru": book.author_ru,
                        "author_original": book.author_in_original_lang
                    }
                    for book in books
                ]
            }

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getBooks")
            return 1

    def getBook(self, id: int) -> dict | int:
        try:
            book = Book.query.filter_by(id=id).first()

            if not book:
                return -1

            return {
                "id": book.id,
                "inventory_num": book.inventory_num,
                "title_ru": book.title_ru,
                "title_original": book.title_original,
                "series": book.series,
                "lang_of_book": book.lang_of_book,
                "lang_original": book.lang_original,
                "author_ru": book.author_ru,
                "author_in_original_lang": book.author_in_original_lang,
                "writing_year": book.writing_year,
                "transfer_year": book.transfer_year,
                "translators": book.translators,
                "explanation_ru": book.explanation_ru,
                "applications": book.applications,
                "dimensions": book.dimensions,
                "publication_year": book.publication_year,
                "edition_num": book.edition_num,
                "publishing_house": book.publishing_house,
                "isbn1": book.isbn1,
                "isbn2": book.isbn2,
                "abstract": book.abstract,
                "cover_photo_uuid": book.cover_photo_uuid,
                "age_of_reader": book.age_of_reader,
                "quantity": book.quantity,
                "pages_quantity": book.pages_quantity,
                "is_on_hand": book.is_on_hand,

                "genre": {
                    "id": book.book_genre.id if book.book_genre else None,
                    "name": book.book_genre.genre_name if book.book_genre else None,
                },
                "document_type": {
                    "id": book.document_type.id if book.document_type else None,
                    "name": book.document_type.type_name if book.document_type else None,
                },
                "condition": {
                    "id": book.condition.id if book.condition else None,
                    "name": book.condition.condition_name if book.condition else None,
                },
                "location": {
                    "id": book.location.id if book.location else None,
                    "name": book.location.place_name if book.location else None,
                },
                "shelve": {
                    "id": book.shelve.id if book.shelve else None,
                    "name": book.shelve.shelve_name if book.shelve else None,
                },
                "topics": [
                    {
                        "id": bt.topic.id,
                        "name": bt.topic.topic_name,
                        "pages": bt.pages
                    } for bt in book.topics_links
                ],
                "keywords": [
                    {
                        "id": kw.id,
                        "keyword": kw.keyword,
                        "pages": kw.pages
                    } for kw in book.keywords
                ],
                "bible_references": [
                    {
                        "id": b.id,
                        "book": b.bible_book.ru if b.bible_book else None,
                        "book_id": b.bible_book_id,
                        "chapter": b.chapter,
                        "verse": b.verse,
                        "pages": b.pages
                    } for b in book.bible_places
                ]
            }

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getBook")
            return 1
