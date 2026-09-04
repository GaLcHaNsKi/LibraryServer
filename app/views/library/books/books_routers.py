from datetime import datetime
from flask import Blueprint, request
from app.views.library.books.books_service import LibraryClient
from app.models import Book, LibrarySyncOperation
from app.views.dropbox_operations import uploadToDropbox
from app.views.common_service import InternalErrorResponse, SuccessResponse, BookNotFoundResponse, LibraryNotFoundResponse
import json

booksBlueprint = Blueprint("books", __name__)

LibraryClient = LibraryClient()


def get_pagination():
    """Bound pagination to prevent expensive unbounded database queries."""
    page = request.args.get("page", 1, int)
    take = request.args.get("take", 10, int)
    if page < 1 or take < 1 or take > 100:
        return None
    return page, take

@booksBlueprint.route("/", methods=["POST"])
def addBookRoute():
    """
    ---
    tags:
      - books
    summary: Add book
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: data
        required: true
        type: string
        description: JSON object with book data containing fields - inventory_num (required, string), title_ru, title_original, series, lang_of_book, lang_original, author_ru, author_in_original_lang, writing_year (integer), transfer_year (integer), translators, explanation_ru, applications, dimensions, publication_year (integer), edition_num (integer), publishing_house, isbn1 (integer), isbn2 (integer), abstract, document_type_id (integer), genre_id (integer), age_of_reader, quantity (integer), location_id (required, integer), shelve_id (required, integer), condition_id (integer), pages_quantity (integer), keywords (array), topics (array), bible_references (array)
      - in: formData
        name: cover-photo
        required: false
        type: file
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    try:
        data = json.loads(request.form.get("data", "{}"))
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in data field"}, 400
    
    libraryId = request.environ["user"]["libraryId"]
    operation_id = data.get("operation_id")
    if operation_id and LibrarySyncOperation.query.filter_by(
        library_id=libraryId, operation_id=operation_id
    ).first():
        return SuccessResponse
    if Book.query.filter_by(library_id=libraryId, inventory_num=data.get("inventory_num", "")).first():
        return {"error_code": "INVENTORY_NUMBER_CONFLICT", "error": "Inventory number already exists"}, 409

    try:
        numeric_fields = ("writing_year", "transfer_year", "publication_year", "edition_num", "isbn1", "isbn2",
                          "document_type_id", "genre_id", "quantity", "condition_id", "pages_quantity")
        numbers = {field: int(data[field]) if data.get(field) not in (None, "") else None for field in numeric_fields}
        location_id = int(data.get("location_id"))
        shelve_id = int(data.get("shelve_id"))
    except (TypeError, ValueError):
        return {"error": "Numeric fields contain an invalid value"}, 400
    
    cover_photo = request.files.get("cover-photo", "")
    photo_result = uploadToDropbox(cover_photo) if cover_photo else None
    if cover_photo and not photo_result:
        return {"error_code": "COVER_UPLOAD_FAILED", "error": "Cover could not be uploaded"}, 422
    photo_url = photo_result.get('url', '') if photo_result else ""

    code = LibraryClient.addBook(
        libraryId=libraryId,
        inventory_num=data.get("inventory_num", ""),
        title_ru=data.get("title_ru", ""),
        title_original=data.get("title_original", ""),
        series=data.get("series", ""),
        lang_of_book=data.get("lang_of_book", ""),
        lang_original=data.get("lang_original", ""),
        author_ru=data.get("author_ru", ""),
        author_in_original_lang=data.get("author_in_original_lang", ""),
        writing_year=numbers["writing_year"],
        transfer_year=numbers["transfer_year"],
        translators=data.get("translators", ""),
        explanation_ru=data.get("explanation_ru", ""),
        applications=data.get("applications", ""),
        dimensions=data.get("dimensions", ""),
        publication_year=numbers["publication_year"],
        edition_num=numbers["edition_num"],
        publishing_house=data.get("publishing_house", ""),
        isbn1=numbers["isbn1"],
        isbn2=numbers["isbn2"],
        abstract=data.get("abstract", ""),
        document_type_id=numbers["document_type_id"],
        book_genre_id=numbers["genre_id"],
        cover_photo_url=photo_url,
        age_of_reader=data.get("age_of_reader", ""),
        quantity=numbers["quantity"] if numbers["quantity"] is not None else 1,
        location_id=location_id,
        shelve_id=shelve_id,
        condition_id=numbers["condition_id"],
        pages_quantity=numbers["pages_quantity"],
        keywords=data.get("keywords", []),
        topics=data.get("topics", []),
        bible_references=data.get("bible_references", []),
        operation_id=operation_id
    )

    if code == 1:
        return InternalErrorResponse
    elif code == 2:
        return {"error": "Выберите место и полку"}, 400
    elif code == 3:
        return {"error": "Выбрано неверное место"}, 400
    elif code == 4:
        return {"error": "Выбрана неверная полка"}, 400
    elif code == 5:
        return {"error": "Заполните инвентарный номер"}, 400
    elif code == 6:
        return {"error_code": "INVENTORY_NUMBER_CONFLICT", "error": "Inventory number already exists"}, 409
    elif code == 7:
        return {"error": "Invalid book quantity, page count, or transfer year"}, 400
    return SuccessResponse


@booksBlueprint.route("/<bookId>/issue", methods=["POST"])
def issueBookRoute(bookId):
    """
    ---
    tags:
      - books
    summary: Issue book
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: path
        name: bookId
        required: true
        type: integer
      - in: formData
        name: name
        required: true
        type: string
      - in: formData
        name: deadline
        required: true
        type: date
        example: "31.12.2026"
    responses:
      200:
        description: Success
      400:
        description: Invalid deadline date
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]
    recipient_name = request.form["name"]
    deadline_str = request.form["deadline"]

    try:
        deadline = datetime.strptime(deadline_str, "%d.%m.%Y")
    except ValueError:
        return {"error": "Expected date for deadline"}, 400

    code = LibraryClient.issueBook(bookId, libraryId, recipient_name, deadline, request.form.get("operation_id"))

    if code == -1:
        return BookNotFoundResponse
    elif code == -2:
        return {"error_code": "BOOK_QUANTITY_CONFLICT", "error": "No copies available"}, 409
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@booksBlueprint.route("/<bookId>/return", methods=["POST"])
def returnBookRoute(bookId):
    """
    ---
    tags:
      - books
    summary: Return book
    parameters:
      - in: path
        name: bookId
        required: true
        type: integer
    responses:
      200:
        description: Success
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]
    code = LibraryClient.returnBook(bookId, libraryId, request.form.get("operation_id"))

    if code == -1:
        return BookNotFoundResponse
    elif code == -2:
        return {"error_code": "ISSUE_NOT_FOUND", "error": "No issue record found"}, 409
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@booksBlueprint.route("/<bookId>", methods=["DELETE"])
def deleteBookRoute(bookId):
    """
    ---
    tags:
      - books
    summary: Delete book
    parameters:
      - in: path
        name: bookId
        required: true
        type: integer
    responses:
      200:
        description: Success
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]
    code = LibraryClient.deleteBook(bookId, libraryId)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@booksBlueprint.route("/<bookId>", methods=["PUT"])
def editBookRoute(bookId):
    """
    ---
    tags:
      - books
    summary: Edit book
    consumes:
      - multipart/form-data
    parameters:
      - in: path
        name: bookId
        required: true
        type: integer
      - in: formData
        name: data
        required: false
        type: string
        description: JSON object with book fields to update
      - in: formData
        name: cover-photo
        required: false
        type: file
    responses:
      200:
        description: Success
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    try:
        data = json.loads(request.form.get("data", "{}"))
    except json.JSONDecodeError:
        data = {}

    # The create endpoint historically uses ``genre_id``, while the model field
    # used by updates is named ``book_genre_id``. Accept the former from older
    # Android clients as well.
    if "genre_id" in data and "book_genre_id" not in data:
        data["book_genre_id"] = data.pop("genre_id")
    
    # Обработка обложки
    cover_photo = request.files.get("cover-photo")
    if cover_photo:
        photo_result = uploadToDropbox(cover_photo)
        if photo_result:
            data["cover_photo_url"] = photo_result.get('url', '')
    
    code = LibraryClient.editBook(bookId, request.environ["user"]["libraryId"], data)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse
    elif code == 2:
        return {"error": "Выберите место и полку"}, 400
    elif code == 3:
        return {"error": "Выбрано неверное место"}, 400
    elif code == 4:
        return {"error": "Выбрана неверная полка"}, 400
    elif code == 5:
        return {"error": "Заполните инвентарный номер"}, 400
    elif code == 6:
        return {"error_code": "INVENTORY_NUMBER_CONFLICT", "error": "Inventory number already exists"}, 409
    elif code == 7:
        return {"error": "Invalid book quantity, page count, or transfer year"}, 400

    return SuccessResponse


@booksBlueprint.route("/all", methods=["POST"])
def getBooksRoute():
    """
    ---
    tags:
      - books
    summary: Get books list with filters
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: query
        name: page
        required: false
        type: integer
      - in: query
        name: take
        required: false
        type: integer
      - in: formData
        name: filters
        required: false
        type: string
    responses:
      200:
        description: Books list
      404:
        description: Library not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]

    pagination = get_pagination()
    if not pagination:
        return {"error": "page must be positive and take must be between 1 and 100"}, 400
    page, take = pagination

    filters_str = request.form.get("filters")

    try:
        filters = json.loads(filters_str) if filters_str else {}
    except json.JSONDecodeError:
        filters = {}

    books = LibraryClient.getBooks(libraryId, page, take, filters)

    if books == -1:
        return LibraryNotFoundResponse
    elif books == 1:
        return InternalErrorResponse

    return books


@booksBlueprint.route("/autofill/all", methods=["POST"])
def getAutofillBooksRoute():
    """Search all libraries for publication data to prefill a new book."""
    pagination = get_pagination()
    if not pagination:
        return {"error": "page must be positive and take must be between 1 and 100"}, 400
    page, take = pagination
    try:
        filters = json.loads(request.form.get("filters", "{}"))
    except json.JSONDecodeError:
        filters = {}

    books = LibraryClient.getAutofillBooks(page, take, filters)
    if books == 1:
        return InternalErrorResponse
    return books


@booksBlueprint.route("/autofill/<bookId>", methods=["GET"])
def getAutofillBookRoute(bookId):
    book = LibraryClient.getAutofillBook(bookId)
    if book == -1:
        return BookNotFoundResponse
    elif book == 1:
        return InternalErrorResponse
    return book


@booksBlueprint.route("/<bookId>", methods=["GET"])
def getBookRoute(bookId):
    """
    ---
    tags:
      - books
    summary: Get book by id
    parameters:
      - in: path
        name: bookId
        required: true
        type: integer
    responses:
      200:
        description: Book
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]
    book = LibraryClient.getBook(bookId, libraryId)
    if book == -1:
        return BookNotFoundResponse
      
    print(book)

    return book


@booksBlueprint.route("/issued/all", methods=["POST"])
def getIssuedBooksRoute():
    """
    ---
    tags:
      - books
    summary: Get issued books list with filters
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - in: query
        name: page
        required: false
        type: integer
      - in: query
        name: take
        required: false
        type: integer
      - in: formData
        name: filters
        required: false
        type: string
    responses:
      200:
        description: Issued books list
      404:
        description: Library not found
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]

    pagination = get_pagination()
    if not pagination:
        return {"error": "page must be positive and take must be between 1 and 100"}, 400
    page, take = pagination

    filters_str = request.form.get("filters")

    try:
        filters = json.loads(filters_str) if filters_str else {}
    except json.JSONDecodeError:
        filters = {}

    books = LibraryClient.getIssuedBooks(libraryId, page, take, filters)

    if books == -1:
        return LibraryNotFoundResponse
    elif books == 1:
        return InternalErrorResponse

    return books


@booksBlueprint.route("/issued/<int:onHandsBookId>", methods=["GET"])
def getIssuedBookRoute(onHandsBookId):
    """
    ---
    tags:
      - books
    summary: Get specific issued book
    parameters:
      - in: path
        name: onHandsBookId
        required: true
        type: integer
    responses:
      200:
        description: Book
      404:
        description: Book not found
      500:
        description: Internal Server Error
    """
    book = LibraryClient.getIssuedBook(onHandsBookId, request.environ["user"]["libraryId"])
    if book == -1:
        return BookNotFoundResponse
    elif book == 1:
        return InternalErrorResponse

    return book
