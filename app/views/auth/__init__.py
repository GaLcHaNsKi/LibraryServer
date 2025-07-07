from flask import Blueprint, request

from app import OWNER, ROLES
from app.views.common_service import getRole
from .auth_service import addUser

authBlueprint = Blueprint("auth", __name__)


@authBlueprint.route("/register", methods=["POST"])
def register():
    """
    Регистрация пользователя. Добавляет в базу данных пользователя, если его nickname ещё нет.
    :return: '3', если nickname уже занят, '0', если пользователь добавлен.
    """
    nickname = request.form["nickname"]
    coded_password = request.form["coded_password"]
    role = request.form["role"]

    if role not in ROLES:
        return {"error": "This role is not exists"}, 404

    lib_name = None
    description = None
    if role == OWNER:
        lib_name = request.form["library-name"]
        description = request.form.get("library-description", "")

    status = addUser(nickname, coded_password, role, lib_name, description)

    if status == "error":  # ошибка
        return {"error": "Internal Server Error"}, 500
    if status == "taken":  # никнейм занят
        return {"error": "Nickname is taken"}, 409

    return {"message": "Success!"}, 200


@authBlueprint.route("/login", methods=["GET"])
def login():
    nickname = request.environ["user"]["nickname"]

    return {"role": getRole(nickname)}, 200
