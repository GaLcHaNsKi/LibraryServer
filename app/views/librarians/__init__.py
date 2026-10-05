from flask import Blueprint, request

from app.views.common_service import LibrarianAlreadyHiredResponse, OfferNotFoundResponse, isExists, InternalErrorResponse, UserNotFoundResponse, SuccessResponse
from app.views.notifications import sendNotify
from app.views.users.users_service import getUserIDByNickname, isHired, acceptOffer, dismissLibrarian, \
    getListOfLibrarians

librariansBlueprint = Blueprint("librarians", __name__)


@librariansBlueprint.route("/", methods=["POST"])
def librarian_control_post():
    """
    ---
    tags:
    - librarians
    summary: Hire librarian
    consumes:
    - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: notificationId
        required: true
        type: string
    responses:
            200:
                description: Success
            404:
                description: Librarian not found
            409:
                description: Librarian already hired
            500:
                description: Internal Server Error
    """
    librarian = request.environ["user"]["nickname"]
    librarianId = request.environ["user"]["id"]
    
    notificationId = request.form.get("notificationId", type=int)
    if notificationId is None:
        return {"error": "notificationId is required"}, 400

    code, directorId = acceptOffer(librarianId, notificationId)
    if code == -1:
        return OfferNotFoundResponse
    if code == -2:
        return ({"error": "You wasn't hired"}, 403)
    if code == -3:
        return LibrarianAlreadyHiredResponse
    if code != 0:
        return InternalErrorResponse

    sendNotify(librarian, directorId, "У вас новый библиотекарь!", f"{librarian} присоединился к вам.",
               "message")

    return SuccessResponse


@librariansBlueprint.route("/", methods=["DELETE"])
def librarians_delete():
    """
    ---
    tags:
    - librarians
    summary: Dismiss librarian
    consumes:
    - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: librarian
        required: true
        type: string
    responses:
            200:
                description: Success
            403:
                description: Not hired
            404:
                description: Librarian not found
            500:
                description: Internal Server Error
    """
    librarian = request.form["librarian"]
    director = request.environ["user"]["nickname"]
    director_id = request.environ["user"]["id"]

    if not isExists(librarian):
        return UserNotFoundResponse

    res = dismissLibrarian(director_id, librarian)
    
    if res == 2:
        return UserNotFoundResponse
    elif res == -1:
        return ({"error": "You are not director!"}, 403)
    elif res == -2:
        return InternalErrorResponse

    sendNotify(director, librarian, "Вы уволены!", f"{director} вас уволил.", "message")

    return SuccessResponse


@librariansBlueprint.route("/", methods=["GET"])
def librarian_control_get_list():
    """
    ---
    tags:
    - librarians
    summary: List librarians for director
    responses:
            200:
                description: Librarians list
            500:
                description: Internal Server Error
    """
    director = request.environ["user"]["nickname"]
    director_id = getUserIDByNickname(director)

    lib_list = getListOfLibrarians(director_id)
    if lib_list == 1:
        return InternalErrorResponse

    return {"data": lib_list}, 200
