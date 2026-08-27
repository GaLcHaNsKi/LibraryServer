from datetime import datetime
from flask import Blueprint, request
from app.views.library.books.books_service import LibraryClient
from app.views.dropbox_operations import uploadToDropbox
from app.views.common_service import InternalErrorResponse, SuccessResponse, BookNotFoundResponse, LibraryNotFoundResponse
import json

booksBlueprint = Blueprint("books", __name__)

LibraryClient = LibraryClient()

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
    
    cover_photo = request.files.get("cover-photo", "")
    photo_result = uploadToDropbox(cover_photo) if cover_photo else None
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
        writing_year=int(data.get("writing_year", 0)) if data.get("writing_year") else None,
        transfer_year=int(data.get("transfer_year", 0)) if data.get("transfer_year") else None,
        translators=data.get("translators", ""),
        explanation_ru=data.get("explanation_ru", ""),
        applications=data.get("applications", ""),
        dimensions=data.get("dimensions", ""),
        publication_year=int(data.get("publication_year", 0)) if data.get("publication_year") else None,
        edition_num=int(data.get("edition_num", 0)) if data.get("edition_num") else None,
        publishing_house=data.get("publishing_house", ""),
        isbn1=int(data.get("isbn1", 0)) if data.get("isbn1") else None,
        isbn2=int(data.get("isbn2", 0)) if data.get("isbn2") else None,
        abstract=data.get("abstract", ""),
        document_type_id=int(data.get("document_type_id")) if data.get("document_type_id") else None,
        book_genre_id=int(data.get("genre_id")) if data.get("genre_id") else None,
        cover_photo_url=photo_url,
        age_of_reader=data.get("age_of_reader", ""),
        quantity=int(data.get("quantity", 1)) if data.get("quantity") else 1,
        location_id=int(data.get("location_id")),
        shelve_id=int(data.get("shelve_id")),
        condition_id=int(data.get("condition_id")) if data.get("condition_id") else None,
        pages_quantity=int(data.get("pages_quantity", 1)) if data.get("pages_quantity") else None,
        keywords=data.get("keywords", []),
        topics=data.get("topics", []),
        bible_references=data.get("bible_references", [])
    )

    if code == 1: 
        return InternalErrorResponse
    elif code == 2:
        return {"error": "Location and shelf are required"}, 400
    elif code == 3:
        return {"error": "Invalid location"}, 400
    elif code == 4:
        return {"error": "Invalid shelf"}, 400

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

    code = LibraryClient.issueBook(bookId, libraryId, recipient_name, deadline)

    if code == -1:
        return BookNotFoundResponse
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
    code = LibraryClient.returnBook(bookId, libraryId)

    if code == -1:
        return BookNotFoundResponse
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
        return {"error": "Location and shelf are required"}, 400
    elif code == 3:
        return {"error": "Invalid location"}, 400
    elif code == 4:
        return {"error": "Invalid shelf"}, 400

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

    page = request.args.get("page", 1, int)
    take = request.args.get("take", 10, int)

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
    page = request.args.get("page", 1, int)
    take = request.args.get("take", 10, int)
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

    page = request.args.get("page", 1, int)
    take = request.args.get("take", 10, int)

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
    book = LibraryClient.getIssuedBook(onHandsBookId)
    if book == -1:
        return BookNotFoundResponse
    elif book == 1:
        return InternalErrorResponse

    return book
