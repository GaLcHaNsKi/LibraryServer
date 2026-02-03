from flask import Blueprint, request

from app.views.users.users_service import deleteUser

usersBlueprint = Blueprint("users", __name__)


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
