from flask import Blueprint, request

from app.views.users.users_service import deleteUser, getUserInfo, editUserNickname
from app.views.common_service import InternalErrorResponse, SuccessResponse, UserNotFoundResponse

usersBlueprint = Blueprint("users", __name__)


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
    newNickname = request.form.get("nickname")

    if not newNickname:
        return {"error": "Nickname is required"}, 400

    code = editUserNickname(userId, newNickname)

    if code == -1:
        return UserNotFoundResponse
    elif code == -2:
        return {"error": "Nickname already taken"}, 409
    elif code == 1:
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
