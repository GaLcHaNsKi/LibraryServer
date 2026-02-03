from flask import Blueprint, request

from app.views.common_service import isExists, InternalErrorResponse, SuccessResponse, UserNotFoundResponse
from app.views.notifications.notifications_service import sendNotify, deleteNotify, getNotify, haveNotify
from app.views.users.users_service import isHired

notificationsBlueprint = Blueprint("notifications", __name__)


@notificationsBlueprint.route("/", methods=["POST"])
def write_notify():
    """
    ---
    tags:
        - notifications
    summary: Send notification
    consumes:
        - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: recipient
        required: true
        type: string
      - in: formData
        name: title
        required: true
        type: string
      - in: formData
        name: text
        required: true
        type: string
      - in: formData
        name: cmd
        required: true
        type: string
    responses:
            200:
                description: Success
            404:
                description: Recipient not found
            500:
                description: Internal Server Error
    """
    author = request.environ["user"]["nickname"]
    recipient = request.form["recipient"]
    title = request.form["title"]
    text = request.form["text"]
    cmd = request.form["cmd"]

    if not isExists(recipient):
        return {"error": "Recipient not found"}, 404

    if sendNotify(author, recipient, title, text, "message"):
        return InternalErrorResponse

    return SuccessResponse


@notificationsBlueprint.route("/offer", methods=["POST"])
def write_offer():
    """
    ---
    tags:
        - notifications
    summary: Send offer notification
    consumes:
        - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: recipient
        required: true
        type: string
      - in: formData
        name: title
        required: true
        type: string
      - in: formData
        name: text
        required: true
        type: string
      - in: formData
        name: cmd
        required: true
        type: string
    responses:
            200:
                description: Success
            404:
                description: Recipient not found
            500:
                description: Internal Server Error
    """
    author = request.environ["user"]["nickname"]
    recipient = request.form["recipient"]
    title = request.form["title"]
    text = request.form["text"]
    cmd = request.form["cmd"]

    if not isExists(recipient):
        return {"error": "Recipient not found"}, 404

    # если директор хочет нанять, то нужно проверить, не нанят ли
    lib_name = isHired(recipient)
    if lib_name == "":
        if sendNotify(author, recipient, title, text, "offer"):
            return InternalErrorResponse
    elif lib_name == 1:
        return InternalErrorResponse
    else:
        return UserNotFoundResponse

    return SuccessResponse


@notificationsBlueprint.route("/<id>", methods=["DELETE"])
def delete_notify(id):
    """
    ---
    tags:
    - notifications
    summary: Delete notification
    parameters:
    - in: path
      name: id
      required: true
      type: integer
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    if deleteNotify(id):
        return InternalErrorResponse

    return SuccessResponse


@notificationsBlueprint.route("/", methods=["GET"])
def notify_get():
    """
    ---
    tags:
        - notifications
    summary: Get notifications
    responses:
            200:
                description: Notifications list
            500:
                description: Internal Server Error
    """
    # для получения уведомлений
    recipient = request.environ["user"]["nickname"]

    ntfs = getNotify(recipient)
    if ntfs == 1:
        return InternalErrorResponse

    return {"data": ntfs}, 200
