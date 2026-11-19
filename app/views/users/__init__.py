from flask import Blueprint, request

from app import OWNER
from app.views.library.library_service import createLibraryForLibrarian
from app.views.users.users_service import deleteUser, getUserInfo, editUser, selfDismissLibrarian
from app.views.common_service import InternalErrorResponse, SuccessResponse, UserNotFoundResponse

usersBlueprint = Blueprint("users", __name__)


@usersBlueprint.route("/library", methods=["POST"])
def create_own_library():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name or len(name) > 20:
        return {"error": "Library name must contain from 1 to 20 characters"}, 400

    result = createLibraryForLibrarian(request.environ["user"]["id"], name, description)
    if result == "created":
        return {"role": OWNER}, 201
    if result == "missing":
        return UserNotFoundResponse
    if result == "forbidden":
        return {"error": "Only an unaffiliated librarian can create a library"}, 403
    if result == "name_taken":
        return {"error": "Library name is taken"}, 409
    return InternalErrorResponse


@usersBlueprint.route("/info", methods=["GET"])
def get_user_info():
    """
    ---
    tags:
        - users
    summary: Get current user info
    responses:
        200:
            description: User info (nickname, role, is_hired, library)
        404:
            description: User not found
        500:
            description: Internal Server Error
    """
    userId = request.environ["user"]["id"]
    result = getUserInfo(userId)

    if result == -1:
        return UserNotFoundResponse
    elif result == 1:
        return InternalErrorResponse

    return result


@usersBlueprint.route("/edit", methods=["PUT"])
def edit_user():
    """
    ---
    tags:
        - users
    summary: Edit current user nickname
    consumes:
        - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: nickname
        required: true
        type: string
    responses:
        200:
            description: Success
        404:
            description: User not found
        409:
            description: Nickname already taken
        500:
            description: Internal Server Error
    """
    userId = request.environ["user"]["id"]
    newNickname = request.form.get("nickname", "").strip()
    newEmail = request.form.get("email")

    if not newNickname:
        return {"error": "Nickname is required"}, 400

    code = editUser(userId, newNickname, newEmail)
    if code == -1:
        return UserNotFoundResponse
    if code == -2:
        return {"error": "Nickname already taken"}, 409
    if code == -3:
        return {"error": "Email already taken"}, 409
    if code == 1:
        return InternalErrorResponse

    return SuccessResponse


@usersBlueprint.route("/dismiss", methods=["POST"])
def self_dismiss():
    """
    ---
    tags:
        - users
    summary: Dismiss self (for hired librarian)
    responses:
        200:
            description: Success
        403:
            description: Not a librarian or not hired
        404:
            description: User not found
        500:
            description: Internal Server Error
    """
    userId = request.environ["user"]["id"]
    code = selfDismissLibrarian(userId)

    if code == -1:
        return UserNotFoundResponse
    elif code == -3:
        return {"error": "You are not a librarian"}, 403
    elif code == -4:
        return {"error": "You are not hired"}, 403
    elif code == -2:
        return InternalErrorResponse

    return SuccessResponse


@usersBlueprint.route("/", methods=["DELETE"])
def delete_user():
    """
    ---
    tags:
        - users
    summary: Delete current user
    responses:
            200:
                description: Success
            403:
                description: Director cannot be deleted
            500:
                description: Internal Server Error
    """
    nickname = request.environ["user"]["nickname"]
    code = deleteUser(nickname)

    if code == 1:
        return {"error": "Internal Server Error"}, 500
    elif code == 2:  # это директор
        return {"error": "You are director!"}, 403

    return {"message": "Success"}, 200
