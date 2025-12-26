from flask import Blueprint, request
from app import OWNER
from app.views.common_service import InternalErrorResponse, SuccessResponse, getRole, isExists, UserNotFoundResponse, ForbiddenResponse
from app.views.notifications import sendNotify
from app.views.users.users_service import getListOfLibrarians, getUserIDByNickname
from app.views.library.library_service import delLibraryByDirectorID, transferLibrary
from app.views.library.places.places_router import placesBlueprint
from app.views.library.books.books_routers import booksBlueprint

libraryBlueprint = Blueprint("library", __name__)

libraryBlueprint.register_blueprint(placesBlueprint, url_prefix="/places")
libraryBlueprint.register_blueprint(booksBlueprint, url_prefix="/books")

@libraryBlueprint.route("/", methods=["DELETE"])
def delete_library():
    director = request.environ["user"]["nickname"]
    director_id = request.environ["user"]["id"]

    if getRole(director) != OWNER:
        return {"error": "Permission denied"}, 403

    librarians = getListOfLibrarians(director_id)

    if delLibraryByDirectorID(director_id):
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
