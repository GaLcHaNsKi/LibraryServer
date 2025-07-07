from datetime import datetime

from flask import Blueprint, request, json, jsonify

from app import OWNER
from app.views.common_service import InternalErrorResponse, SuccessResponse, BookNotFoundResponse, \
    LibraryNotFoundResponse, getRole, isExists, LibrarianNotFoundResponse, ForbiddenResponse
from app.views.library.dropbox_operations import uploadToDropbox
from app.views.library.library_service import LibraryClient
from app.views.notifications import sendNotify
from app.views.users.users_service import getListOfLibrarians, getUserIDByNickname

libraryBlueprint = Blueprint("library", __name__)
LibraryClient = LibraryClient()


@libraryBlueprint.route("/books", methods=["POST"])
def add_book_to_library():
    inventory_num = request.form["inventory_num"]
    lib_name = request.environ["user"]["library"]

    cover_photo = request.files.get("cover-photo", "")
    photo_uuid = ""
    if cover_photo:
        photo_uuid = uploadToDropbox(cover_photo)

    code = LibraryClient.addBook(
        library=lib_name,
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
        document_type_id=int(request.form.get("document_type_id", "0")) if request.form.get(
            "document_type_id") else None,
        book_genre_id=int(request.form.get("book_genre_id", "0")) if request.form.get("book_genre_id") else None,
        cover_photo_uuid=photo_uuid,
        age_of_reader=request.form.get("age_of_reader", ""),
        quantity=int(request.form.get("quantity", "0")) if request.form.get("quantity") else None,
        location_id=int(request.form.get("location_id", "0")) if request.form.get("location_id") else None,
        shelve_id=int(request.form.get("shelve_id", "0")) if request.form.get("shelve_id") else None,
        condition_id=int(request.form.get("condition_id", "0")) if request.form.get("condition_id") else None,
        pages_quantity=int(request.form.get("pages_quantity", "1")) if request.form.get("pages_quantity") else None,
        keywords=json.loads(request.form.get("keywords", "[]")),
        topics=json.loads(request.form.get("topics", "[]")),
        bible_references=json.loads(request.form.get("bible_references", "[]"))
    )

    if code: return InternalErrorResponse

    return SuccessResponse


@libraryBlueprint.route("/books/<bookId>/issue", methods=["POST"])
def issue_book(bookId):
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


@libraryBlueprint.route("/books/<bookId>/return", methods=["POST"])
def return_book(bookId):
    deadline = request.form["deadline"]

    try:
        datetime.strptime(deadline, "%d.%m.%Y")
    except ValueError:
        return {"error": "Expected date for deadline"}, 400

    code = LibraryClient.returnBook(bookId)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@libraryBlueprint.route("/books/<bookId>", methods=["DELETE"])
def delete_book(bookId):
    code = LibraryClient.deleteBook(bookId)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@libraryBlueprint.route("/books/<bookId>", methods=["PUT"])
def edit_book(bookId):
    changes = request.json()
    code = LibraryClient.editBook(bookId, changes)

    if code == -1:
        return BookNotFoundResponse
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@libraryBlueprint.route("/books/all", methods=["POST"])
async def get_books():
    library = request.environ["user"]["library"]

    page = request.args.get("page", 1)
    take = request.args.get("take", 10)

    filters = await jsonify(request.form.get("filters")).json

    books = LibraryClient.getBooks(library, page, take, filters)
    if books == -1:
        return LibraryNotFoundResponse

    return books


@libraryBlueprint.route("/books/<bookId>", methods=["GET"])
def get_book(bookId):
    book = LibraryClient.getBook(bookId)
    if book == -1:
        return BookNotFoundResponse

    return book


@libraryBlueprint.route("/places", methods=["GET"])
def sendPlacesList():
    library = request.environ["user"]["library"]

    places_list = LibraryClient.getPlaces(library)

    if places_list == 1:
        return InternalErrorResponse

    return places_list


@libraryBlueprint.route("/", methods=["DELETE"])
def delete_library():
    director = request.environ["user"]["nickname"]
    director_id = request.environ["user"]["id"]

    if getRole(director) != OWNER:
        return {"error": "Permission denied"}, 403

    librarians = getListOfLibrarians(director_id)

    if LibraryClient.delLibraryByDirectorID(director_id):
        return InternalErrorResponse

    # оповещение библиотекарям
    for i in range(1, librarians["quant"] + 1):
        sendNotify(director, librarians[str(i)], "Беда!", f"{director} удалил библиотеку.", "send")

    return SuccessResponse


@libraryBlueprint.route("/transfer", methods=["PUT"])
def transfer_library():
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    successor = request.form["successor"]
    successor_id = isExists(successor)

    if not successor_id:
        return LibrarianNotFoundResponse

    code = LibraryClient.transferLibrary(director_id, successor_id)

    if code == 1:
        return InternalErrorResponse
    elif code == 2:
        return ForbiddenResponse

    # оповещение библиотекарям
    for librarian in getListOfLibrarians(successor_id):
        sendNotify(director, librarian, "У вас новый директор!",
                   f"{director} передал свою библиотеку пользователю {successor}.", "send")

    return SuccessResponse
