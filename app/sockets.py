from flask import request
from flask_socketio import join_room, leave_room

from app import socketio, db
from app.models import User
from app.views.common_service import isExists
from app.views.logs import elog


# Хранение подключённых пользователей: {user_id: sid}
connected_users = {}


@socketio.on("connect")
def handle_connect():
    """
    Клиент подключается с auth: {"nickname": "...", "password": "..."}
    Присоединяется к персональной комнате user_{id}.
    """
    auth = request.args
    nickname = auth.get("nickname", "")
    password = auth.get("password", "")

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
