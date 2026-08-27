from flask import Blueprint, request
from app import OWNER
from app.views.common_service import InternalErrorResponse, SuccessResponse, getRole, isExists, UserNotFoundResponse, ForbiddenResponse, LibraryNotFoundResponse
from app.views.notifications import sendNotify
from app.views.users.users_service import getListOfLibrarians, getUserIDByNickname
from app.views.library.library_service import delLibraryByDirectorID, transferLibrary, getLibraryInfo, editLibrary
from app.views.library.places.places_router import placesBlueprint
from app.views.library.books.books_routers import booksBlueprint

libraryBlueprint = Blueprint("library", __name__)

libraryBlueprint.register_blueprint(placesBlueprint, url_prefix="/places")
libraryBlueprint.register_blueprint(booksBlueprint, url_prefix="/books")


@libraryBlueprint.route("/info", methods=["GET"])
def get_library_info():
    """
    ---
    tags:
        - library
    summary: Get current library info
    responses:
        200:
            description: Library info
        404:
            description: Library not found
        500:
            description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]

    result = getLibraryInfo(libraryId)

    if result == -1:
        return LibraryNotFoundResponse
    elif result == 1:
        return InternalErrorResponse

    return result


@libraryBlueprint.route("/edit", methods=["PUT"])
def edit_library():
    """
    ---
    tags:
        - library
    summary: Edit library name and description (director only)
    consumes:
        - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: name
        required: false
        type: string
      - in: formData
        name: description
        required: false
        type: string
    responses:
        200:
            description: Success
        403:
            description: Permission denied
        404:
            description: Library not found
        500:
            description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]
    directorId = request.environ["user"]["id"]

    changes = {}
    if request.form.get("name"):
        changes["name"] = request.form["name"]
    if request.form.get("description"):
        changes["description"] = request.form["description"]

    if not changes:
        return {"error": "No changes provided"}, 400

    code = editLibrary(libraryId, directorId, changes)

    if code == -1:
        return LibraryNotFoundResponse
    elif code == -2:
        return ForbiddenResponse
    elif code == 1:
        return InternalErrorResponse

    return SuccessResponse


@libraryBlueprint.route("/", methods=["DELETE"])
def delete_library():
    """
    ---
    tags:
        - library
    summary: Delete library (director only)
    responses:
            200:
                description: Success
            403:
                description: Permission denied
            500:
                description: Internal Server Error
    """
    director = request.environ["user"]["nickname"]
    director_id = request.environ["user"]["id"]

    if getRole(director) != OWNER:
        return {"error": "Permission denied"}, 403

    librarians = getListOfLibrarians(director_id)

    if delLibraryByDirectorID(director_id):
        return InternalErrorResponse

    # оповещение библиотекарям
    if isinstance(librarians, list):
        for librarian in librarians:
            sendNotify(director, librarian, "Беда!", f"{director} удалил библиотеку.", "send")

    return SuccessResponse


@libraryBlueprint.route("/transfer", methods=["PUT"])
def transfer_library():
    """
    ---
    tags:
        - library
    summary: Transfer library to librarian
    consumes:
        - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: successor
        required: true
        type: string
    responses:
            200:
                description: Success
            403:
                description: Forbidden
            404:
                description: User not found
            500:
                description: Internal Server Error
    """
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    successor = request.form["successor"]
    successor_id = isExists(successor)

    if not successor_id:
        return UserNotFoundResponse

    code =  transferLibrary(director_id, successor_id)

    if code == 1:
        return InternalErrorResponse
    elif code == 2:
        return ForbiddenResponse

    # оповещение библиотекарям
    for librarian in getListOfLibrarians(successor_id):
        sendNotify(director, librarian, "У вас новый директор!",
                   f"{director} передал свою библиотеку пользователю {successor}.", "send")

    return SuccessResponse
