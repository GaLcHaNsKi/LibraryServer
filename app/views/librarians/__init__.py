from flask import Blueprint, request

from app.views.common_service import isExists, InternalErrorResponse, UserNotFoundResponse, SuccessResponse
from app.views.notifications import sendNotify
from app.views.users.users_service import getUserIDByNickname, isHired, hireLibrarian, dismissLibrarian, \
    getListOfLibrarians

librariansBlueprint = Blueprint("librarians", __name__)


@librariansBlueprint.route("/", methods=["POST"])
def librarian_control_post():
    """
        Для нанятия библиотекарей
    """
    librarian = request.form["librarian"]
    director = request.environ["user"]["nickname"]

    director_id = getUserIDByNickname(director)

    if not isExists(librarian):
        return {"error": "Librarian not found"}, 404

    lib_name = isHired(librarian)
    if lib_name == 1:
        return InternalErrorResponse
    elif lib_name == 2:
        return UserNotFoundResponse

    if hireLibrarian(director_id, librarian): return InternalErrorResponse

    sendNotify(librarian, director, "У вас новый библиотекарь!", f"{librarian} присоединился к вам.",
               "message")

    return SuccessResponse


@librariansBlueprint.route("/", methods=["DELETE"])
def librarians_delete():
    """
        Для увольнения библиотекарей
    """
    librarian = request.form["librarian"]
    director = request.environ["user"]["nickname"]

    if not isExists(librarian):
        return UserNotFoundResponse

    if dismissLibrarian(librarian): return InternalErrorResponse

    sendNotify(director, librarian, "Вы уволены!", f"{director} вас уволил.", "message")

    return SuccessResponse


@librariansBlueprint.route("/", methods=["GET"])
def librarian_control_get_list():
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    lib_list = getListOfLibrarians(director_id)
    if lib_list == 1:
        return InternalErrorResponse

    return {"data": lib_list}, 200
