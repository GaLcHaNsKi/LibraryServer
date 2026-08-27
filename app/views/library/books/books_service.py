from datetime import datetime

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
                 cover_photo_url=None,
                 age_of_reader="",
                 quantity=1,
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

            if not inventory_num or not str(inventory_num).strip():
                return 5  # Inventory number is required

            if not location_id or not shelve_id:
                return 2  # Missing location or shelf

            place = Place.query.filter_by(id=location_id, library_id=libraryId).first()
            if not place:
                return 3  # Invalid location

            shelf = Shelf.query.filter_by(id=shelve_id, place_id=location_id).first()
            if not shelf:
                return 4  # Invalid shelf

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
                cover_photo_url=cover_photo_url,
                age_of_reader=age_of_reader,
                quantity=quantity,
                location_id=location_id,
                shelve_id=shelve_id,
                condition_id=condition_id,
                pages_quantity=pages_quantity
            )
            db.session.add(new_book)
            db.session.flush()  # Ensure book.id is available for related records

            # Ключевые слова, темы и библейские ссылки — переиспользуем те же
            # методы, что и при редактировании (списки уже разобраны из JSON).
            if keywords:
                self._updateKeywords(new_book, keywords)
            if topics:
                self._updateTopics(new_book, topics)
            if bible_references:
                self._updateBibleReferences(new_book, bible_references)

            # Commit all changes
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()  # Roll back on error
            elog(e, file="book_service", function="addBook")
            return 1

    def issueBook(self, bookId, libraryId, recipient_name, deadline):
        """
        Выдает книгу: уменьшает количество на 1 и добавляет запись в OnHandsBook.
        """
        try:
            # Get recipient_id
            recipient_id = isExists(recipient_name)

            # Get book
            book = Book.query.filter_by(id=bookId, library_id=libraryId).first()
            if not book:
                return -1

            # Check if quantity > 0
            if book.quantity <= 0:
                return -2  # No books available

            # Decrease quantity
            book.quantity -= 1

            # Create OnHandsBook record
            on_hands_book = OnHandsBook(
                book_id=book.id,
                recipient_name=recipient_name,
                recipient_id=recipient_id or None,  # Convert 0 to None for nullable field
                issue_date=datetime.now(),
                return_date=deadline
            )
            db.session.add(on_hands_book)

            # Commit changes
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()  # Roll back on error
            elog(e, "book_service", "issueBook")
            return 1

    def returnBook(self, bookId, libraryId) -> int:
        """
        Возвращает книгу: увеличивает количество на 1 и удаляет запись из OnHandsBook.
        """
        try:
            # Get book
            book = Book.query.filter_by(id=bookId, library_id=libraryId).first()
            if not book:
                return -1

            # Check if there's a record in OnHandsBook
            on_hands = OnHandsBook.query.filter_by(book_id=book.id).first()
            if not on_hands:
                return -2  # No issue record found

            # Delete the OnHandsBook record
            db.session.delete(on_hands)

            # Increase quantity
            book.quantity += 1

            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "returnBook")
            return 1

    def _applyFilters(self, query, filters_: dict):
        """
        Применяет фильтры к запросу.
        Используется как в getBooks, так и в getIssuedBooks.
        
        Returns:
            - query: обновленный запрос
            - error_code: 0 если успешно, 1 если ошибка
        """
        try:
            if not filters_:
                return query, 0

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
                            return query, 1  # Некорректный тип
                    else:
                        return query, 1  # Неподдерживаемый тип фильтра
            
            return query, 0

        except Exception as e:
            elog(e, "book_service", "_applyFilters")
            return query, 1

    def _buildBookResponse(self, book: Book) -> dict:
        """
        Строит стандартный ответ с данными о книге (без деталей выдачи).
        """
        return {
            "id": book.id,
            "inventory_num": book.inventory_num,
            "title_ru": book.title_ru,
            "title_original": book.title_original,
            "genre": book.book_genre.genre_name if book.book_genre else None,
            "author_ru": book.author_ru,
            "author_original": book.author_in_original_lang,
            "cover_photo_url": book.cover_photo_url,
            "quantity": book.quantity,
        }

    def _buildAutofillBookResponse(self, book: Book) -> dict:
        """Fields that describe a publication, rather than a library copy."""
        return {
            "id": book.id,
            "title_ru": book.title_ru,
            "title_original": book.title_original,
            "genre": book.book_genre.genre_name if book.book_genre else None,
            "author_ru": book.author_ru,
            "author_original": book.author_in_original_lang,
            "cover_photo_url": book.cover_photo_url,
        }

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

    def deleteBook(self, bookId: int, libraryId: int) -> int:
        """
        Удаляет книгу по ID.
        Args:
            bookId (int): ID книги
            libraryId (int): ID библиотеки
        Returns:
            int: 0 — успех, 1 — ошибка, -1 - книга не найдена
        """
        try:
            book = Book.query.filter_by(id=bookId, library_id=libraryId).first()
            if not book:
                return -1  # Книга не найдена

            db.session.delete(book)
            db.session.commit()
            return 0

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "deleteBook")
            return 1

    # Поля, которые можно редактировать
    editable_fields = {
        "inventory_num", "title_ru", "title_original", "series", "lang_of_book",
        "lang_original", "author_ru", "author_in_original_lang", "writing_year",
        "transfer_year", "translators", "explanation_ru", "applications", "dimensions",
        "publication_year", "edition_num", "publishing_house", "isbn1", "isbn2",
        "abstract", "document_type_id", "book_genre_id", "cover_photo_url",
        "age_of_reader", "quantity", "location_id", "shelve_id", "condition_id",
        "pages_quantity"
    }

    def editBook(self, bookId: int, libraryId: int, changes: dict):
        """
        Updates a book's fields.
        Args:
            bookId (int): ID книги
            libraryId (int): ID библиотеки
            changes: Data to change.
        """
        try:
            book = Book.query.filter_by(id=bookId, library_id=libraryId).first()
            if not book:
                return -1  # Book not found

            if "inventory_num" in changes and (not changes["inventory_num"] or not str(changes["inventory_num"]).strip()):
                return 5  # Inventory number is required

            if "location_id" in changes or "shelve_id" in changes:
                loc_id = changes.get("location_id", book.location_id)
                sh_id = changes.get("shelve_id", book.shelve_id)
                
                if not loc_id or not sh_id:
                    return 2

                place = Place.query.filter_by(id=loc_id, library_id=libraryId).first()
                if not place:
                    return 3
                    
                shelf = Shelf.query.filter_by(id=sh_id, place_id=loc_id).first()
                if not shelf:
                    return 4

            # Update book fields
            for field, value in changes.items():
                if field in self.editable_fields:
                    setattr(book, field, value)
                elif field == "topics":
                    self._updateTopics(book, value)
                elif field == "keywords":
                    self._updateKeywords(book, value)
                elif field in ("bibleReferences", "bible_references"):
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
                    name: str
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
                        topic_name=item["name"],
                        pages=item.get("pages", "")
                    )
                    db.session.add(new_link)
                elif link_id in existing_links:
                    # Обновление существующей связи
                    link = existing_links[link_id]
                    link.topic_name = item["name"]
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
        """
        Получает список доступных (не выданных) книг с фильтрами.
        Исключает книги с quantity = 0.
        """
        try:
            query = Book.query

            if libraryId:   # если указана библиотека, то ищем в ней
                query = Book.query.filter_by(library_id=libraryId)

            # Exclude books with quantity = 0
            query = query.filter(Book.quantity > 0)

            # Apply filters using helper function
            query, error = self._applyFilters(query, filters_)
            if error:
                return 1

            total = query.count()
            offset = (page - 1) * take
            
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
                "data": [self._buildBookResponse(book) for book in books]
            }

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getBooks")
            return 1

    def getBook(self, id: int, libraryId: int) -> dict | int:
        try:
            book = Book.query.filter_by(id=id, library_id=libraryId).first()

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
                "cover_photo_url": book.cover_photo_url,
                "age_of_reader": book.age_of_reader,
                "quantity": book.quantity,
                "pages_quantity": book.pages_quantity,

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
                        "id": bt.id,
                        "name": bt.topic_name,
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

    def getAutofillBooks(self, page: int = 1, take: int = 10, filters_: dict = None) -> dict | int:
        """Search publications across all libraries for creating a new copy."""
        try:
            query, error = self._applyFilters(Book.query, filters_)
            if error:
                return 1

            total = query.count()
            offset = (page - 1) * take
            books = query.options(joinedload(Book.book_genre)).order_by(Book.title_ru).offset(offset).limit(take).all()
            return {
                "pages": (total + take - 1) // take,
                "data": [self._buildAutofillBookResponse(book) for book in books]
            }
        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getAutofillBooks")
            return 1

    def getAutofillBook(self, id: int) -> dict | int:
        """Return only publication-level fields; never expose copy/location data."""
        try:
            book = Book.query.filter_by(id=id).first()
            if not book:
                return -1

            return {
                "id": book.id,
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
                "cover_photo_url": book.cover_photo_url,
                "age_of_reader": book.age_of_reader,
                "pages_quantity": book.pages_quantity,
                "genre": {
                    "id": book.book_genre.id if book.book_genre else None,
                    "name": book.book_genre.genre_name if book.book_genre else None,
                },
                "document_type": {
                    "id": book.document_type.id if book.document_type else None,
                    "name": book.document_type.type_name if book.document_type else None,
                },
            }
        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getAutofillBook")
            return 1

    def getIssuedBooks(self, libraryId: int | None, page: int = 1, take: int = 10, filters_: dict = None) -> dict | int:
        """
        Получает список выданных книг с фильтрами.
        Возвращает данные о книге + информацию о выдаче.
        """
        try:
            # Start with Book query
            query = Book.query

            if libraryId:
                query = query.filter(Book.library_id == libraryId)

            # Apply filters using helper function
            query, error = self._applyFilters(query, filters_)
            if error:
                return 1

            # Join with OnHandsBook to get only issued books
            query = query.join(OnHandsBook, Book.id == OnHandsBook.book_id)

            total = query.count()
            offset = (page - 1) * take
            
            # Eager load relationships
            query = query.options(
                joinedload(Book.book_genre),
                joinedload(Book.location),
                joinedload(Book.shelve),
                joinedload(Book.condition),
                joinedload(Book.document_type)
            )
            
            books = query.order_by(Book.title_ru).offset(offset).limit(take).all()

            data = []
            for book in books:
                # Get all on_hands records for this book
                on_hands_records = OnHandsBook.query.filter_by(book_id=book.id).all()
                for on_hands in on_hands_records:
                    book_data = self._buildBookResponse(book)
                    # Add issued information
                    book_data.update({
                        "issue_info": {
                            "id": on_hands.id,
                            "recipient_name": on_hands.recipient_name,
                            "recipient_id": on_hands.recipient_id,
                            "issue_date": on_hands.issue_date.isoformat() if on_hands.issue_date else None,
                            "return_date": on_hands.return_date.isoformat() if on_hands.return_date else None,
                        }
                    })
                    data.append(book_data)

            return {
                "pages": (total + take - 1) // take,
                "data": data
            }

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getIssuedBooks")
            return 1

    def getIssuedBook(self, onHandsBookId: int) -> dict | int:
        """
        Получает одну выданную книгу по ID записи в OnHandsBook.
        Возвращает полные данные о книге + информацию о выдаче.
        """
        try:
            on_hands = OnHandsBook.query.filter_by(id=onHandsBookId).first()
            if not on_hands:
                return -1  # Record not found

            book = Book.query.filter_by(id=on_hands.book_id).first()
            if not book:
                return -1  # Book not found

            # Build full book response
            response = {
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
                "cover_photo_url": book.cover_photo_url,
                "age_of_reader": book.age_of_reader,
                "quantity": book.quantity,
                "pages_quantity": book.pages_quantity,

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
                        "id": bt.id,
                        "name": bt.topic_name,
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
                ],
                "issue_info": {
                    "id": on_hands.id,
                    "recipient_name": on_hands.recipient_name,
                    "recipient_id": on_hands.recipient_id,
                    "issue_date": on_hands.issue_date.isoformat() if on_hands.issue_date else None,
                    "return_date": on_hands.return_date.isoformat() if on_hands.return_date else None,
                }
            }

            return response

        except Exception as e:
            db.session.rollback()
            elog(e, "book_service", "getIssuedBook")
            return 1
