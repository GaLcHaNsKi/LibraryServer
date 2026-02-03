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
        name: inventory_num
        required: true
        type: string
      - in: formData
        name: title_ru
        required: false
        type: string
      - in: formData
        name: title_original
        required: false
        type: string
      - in: formData
        name: series
        required: false
        type: string
      - in: formData
        name: lang_of_book
        required: false
        type: string
      - in: formData
        name: lang_original
        required: false
        type: string
      - in: formData
        name: author_ru
        required: false
        type: string
      - in: formData
        name: author_in_original_lang
        required: false
        type: string
      - in: formData
        name: writing_year
        required: false
        type: integer
      - in: formData
        name: transfer_year
        required: false
        type: integer
      - in: formData
        name: translators
        required: false
        type: string
      - in: formData
        name: explanation_ru
        required: false
        type: string
      - in: formData
        name: applications
        required: false
        type: string
      - in: formData
        name: dimensions
        required: false
        type: string
      - in: formData
        name: publication_year
        required: false
        type: integer
      - in: formData
        name: edition_num
        required: false
        type: integer
      - in: formData
        name: publishing_house
        required: false
        type: string
      - in: formData
        name: isbn1
        required: false
        type: integer
      - in: formData
        name: isbn2
        required: false
        type: integer
      - in: formData
        name: abstract
        required: false
        type: string
      - in: formData
        name: document_type
        required: false
        type: string
      - in: formData
        name: genre
        required: false
        type: string
      - in: formData
        name: cover-photo
        required: false
        type: file
      - in: formData
        name: age_of_reader
        required: false
        type: string
      - in: formData
        name: quantity
        required: false
        type: integer
      - in: formData
        name: location
        required: true
        type: string
      - in: formData
        name: shelve
        required: true
        type: string
      - in: formData
        name: condition
        required: false
        type: string
      - in: formData
        name: pages_quantity
        required: false
        type: integer
      - in: formData
        name: keywords
        required: false
        type: string
      - in: formData
        name: topics
        required: false
        type: string
      - in: formData
        name: bible_references
        required: false
        type: string
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    inventory_num = request.form.get("inventory_num")
    libraryId = request.environ["user"]["libraryId"]
    
    print(request.form)

    cover_photo = request.files.get("cover-photo", "")
    photo_uuid = ""
    if cover_photo:
        photo_uuid = uploadToDropbox(cover_photo)

    code = LibraryClient.addBook(
        libraryId=libraryId,
        inventory_num=inventory_num,
        title_ru=request.form.get("title_ru", ""),
        title_original=request.form.get("title_original", ""),
        series=request.form.get("series", ""),
        lang_of_book=request.form.get("lang_of_book", ""),
        lang_original=request.form.get("lang_original", ""),
        author_ru=request.form.get("author_ru", ""),
        author_in_original_lang=request.form.get("author_in_original_lang", ""),
        writing_year=int(request.form.get("writing_year", "0")) if request.form.get("writing_year") else None,
        transfer_year=int(request.form.get("transfer_year", "0")) if request.form.get("transfer_year") else None,
        translators=request.form.get("translators", ""),
        explanation_ru=request.form.get("explanation_ru", ""),
        applications=request.form.get("applications", ""),
        dimensions=request.form.get("dimensions", ""),
        publication_year=int(request.form.get("publication_year", "0")) if request.form.get(
            "publication_year") else None,
        edition_num=int(request.form.get("edition_num", "0")) if request.form.get("edition_num") else None,
        publishing_house=request.form.get("publishing_house", ""),
        isbn1=int(request.form.get("isbn1", "0")) if request.form.get("isbn1") else None,
        isbn2=int(request.form.get("isbn2", "0")) if request.form.get("isbn2") else None,
        abstract=request.form.get("abstract", ""),
        document_type_id=int(request.form.get("document_type")["id"]) if request.form.get("document_type") else None,
        book_genre_id=int(request.form.get("genre")["id"]) if request.form.get("genre") else None,
        cover_photo_uuid=photo_uuid,
        age_of_reader=request.form.get("age_of_reader", ""),
        quantity=int(request.form.get("quantity", "0")) if request.form.get("quantity") else None,
        location_id=int(request.form.get("location")["id"]),
        shelve_id=int(request.form.get("shelve")["id"]),
        condition_id=int(request.form.get("condition")["id"]) if request.form.get("condition") else None,
        pages_quantity=int(request.form.get("pages_quantity", "1")) if request.form.get("pages_quantity") else None,
        keywords=json.loads(request.form.get("keywords", "[]")),
        topics=json.loads(request.form.get("topics", "[]")),
        bible_references=json.loads(request.form.get("bible_references", "[]"))
    )

    if code: return InternalErrorResponse

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
    recipient_name = request.form["name"]
    deadline = request.form["deadline"]

    try:
        datetime.strptime(deadline, "%d.%m.%Y")
    except ValueError:
        return {"error": "Expected date for deadline"}, 400

    code = LibraryClient.issueBook(bookId, recipient_name, deadline)

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
    code = LibraryClient.returnBook(bookId)

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
    code = LibraryClient.deleteBook(bookId)

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
      - application/json
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
    changes = request.get_json(silent=True) or {}
    code = LibraryClient.editBook(bookId, changes)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse

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
    book = LibraryClient.getBook(bookId)
    if book == -1:
        return BookNotFoundResponse

    return book