from flask import request
from flask_socketio import join_room, leave_room

from app import socketio, db
from app.models import User
from app.views.common_service import isExists
from app.views.logs import elog


# Хранение подключённых пользователей: {user_id: sid}
connected_users = {}


def _basic_auth_credentials(authorization):
    """Разбирает заголовок 'Authorization: Basic base64(nickname:password)'.

    Возвращает (nickname, password) или (None, None), если заголовок
    отсутствует либо имеет неверный формат.
    """
    import base64

    if not authorization:
        return None, None

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "basic":
        return None, None

    try:
        decoded = base64.b64decode(parts[1]).decode("utf-8")
    except Exception:
        return None, None

    if ":" not in decoded:
        return None, None

    nickname, password = decoded.split(":", 1)
    return nickname, password


@socketio.on("connect")
def handle_connect():
    """
    Клиент подключается с заголовком 'Authorization: Basic base64(nick:pass)'.
    Присоединяется к персональной комнате user_{id}.
    """
    nickname, password = _basic_auth_credentials(request.headers.get("Authorization"))

    if not nickname or not password:
        return False  # Отклоняем подключение

    user_id = isExists(nickname, password)
    if not user_id or user_id < 0:
        return False  # Отклоняем подключение

    room = f"user_{user_id}"
    join_room(room)
    connected_users[user_id] = request.sid
    print(f"[Socket] {nickname} connected, room: {room}")


@socketio.on("disconnect")
def handle_disconnect():
    """
    Удаляем пользователя из списка подключённых при отключении.
    """
    sid = request.sid
    user_id = None
    for uid, s in connected_users.items():
        if s == sid:
            user_id = uid
            break

    if user_id:
        leave_room(f"user_{user_id}")
        del connected_users[user_id]
        print(f"[Socket] user_{user_id} disconnected")


def emit_notification(recipient_id: int, data: dict):
    """
    Отправляет уведомление в комнату пользователя через WebSocket.
    Вызывается из notifications_service.sendNotify().
    """
    room = f"user_{recipient_id}"
    socketio.emit("notification", data, room=room)
