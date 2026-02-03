from flask import Blueprint, request

from app import OWNER, ROLES
from app.views.common_service import getRole
from .auth_service import addUser

authBlueprint = Blueprint("auth", __name__)


@authBlueprint.route("/register", methods=["POST"])
def register():
    """
    ---
    tags:
    - auth
    summary: Register user
    consumes:
    - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: nickname
        required: true
        type: string
      - in: formData
        name: password
        required: true
        type: string
      - in: formData
        name: role
        required: true
        type: string
        enum:
          - OWNER
          - LIBRARIAN
          - READER
        description: User role
      - in: formData
        name: library-name
        required: false
        type: string
      - in: formData
        name: library-description
        required: false
        type: string
    responses:
            200:
                description: Success
            404:
                description: Invalid role
            409:
                description: Nickname is taken
            500:
                description: Internal Server Error
    security: []
    """
    nickname = request.form["nickname"]
    password = request.form["password"]
    role = request.form["role"]

    if role not in ROLES:
        return {"error": "This role is not exists"}, 404

    lib_name = None
    description = None
    if role == OWNER:
        lib_name = request.form["library-name"]
        description = request.form.get("library-description", "")

    status = addUser(nickname, password, role, lib_name, description)

    if status == "error":  # ошибка
        return {"error": "Internal Server Error"}, 500
    if status == "taken":  # никнейм занят
        return {"error": "Nickname is taken"}, 409

    return {"message": "Success!"}, 200


@authBlueprint.route("/login", methods=["GET"])
def login():
    """
    ---
    tags:
    - auth
    summary: Login (basic auth)
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        description: Basic Auth credentials (base64 encoded username:password)
    responses:
            200:
                description: User role
            401:
                description: Unauthorized
            404:
                description: User not found
            500:
                description: Internal Server Error
    security:
      - basicAuth: []
    """
    nickname = request.environ["user"]["nickname"]

    return {"role": getRole(nickname)}, 200
