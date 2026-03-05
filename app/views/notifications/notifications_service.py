from app import db
from app.models import User, Notification, NotificationSetting
from app.views.logs import elog
from app.sockets import emit_notification
from sqlalchemy.orm import aliased


def get_notification_settings(user_id):
    try:
        setting = NotificationSetting.query.filter_by(user_id=user_id).first()
        if not setting:
            return {
                "notify_before_days": 1,
                "notify_after_days": 0,
                "is_every_day": False
            }
        return {
            "notify_before_days": setting.notify_before_days,
            "notify_after_days": setting.notify_after_days,
            "is_every_day": setting.is_every_day
        }
    except Exception as e:
        elog(e, file="notifications_service", function="get_notification_settings")
        return 1


def set_notification_settings(user_id, notify_before_days, notify_after_days, is_every_day):
    try:
        setting = NotificationSetting.query.filter_by(user_id=user_id).first()
        if not setting:
            setting = NotificationSetting(
                user_id=user_id,
                notify_before_days=notify_before_days,
                notify_after_days=notify_after_days,
                is_every_day=is_every_day
            )
            db.session.add(setting)
        else:
            setting.notify_before_days = notify_before_days
            setting.notify_after_days = notify_after_days
            setting.is_every_day = is_every_day
        db.session.commit()
        return 0
    except Exception as e:
        db.session.rollback()
        elog(e, file="notifications_service", function="set_notification_settings")
        return 1
    


def sendNotify(author, recipient, title, content, type_):
    try:
        # Get author and recipient IDs
        author_user = User.query.filter_by(nickname=author).first()
        
        recipient_user = None
        if isinstance(recipient, int):
            recipient_user = User.query.get(recipient)
        else:
            recipient_user = User.query.filter_by(nickname=recipient).first()
        
        if not author_user or not recipient_user:
            return -1  # User(s) not found

        # Create notification
        notification = Notification(
            author_id=author_user.id,
            recipient_id=recipient_user.id,
            title=title,
            content=content,
            type=type_
        )
        db.session.add(notification)

        # Commit changes
        db.session.commit()

        # Отправляем уведомление через WebSocket
        emit_notification(recipient_user.id, {
            "id": notification.id,
            "author": author,
            "title": title,
            "text": content,
            "type": type_
        })

        return 0

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="notifications_service", function="sendNotify")
        return 1


def deleteNotify(id: int):
    try:
        # Find notification by id
        notification = Notification.query.get(id)
        if not notification:
            return 1  # Notification not found

        # Delete notification
        db.session.delete(notification)

        # Commit changes
        db.session.commit()
        return 0

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="notifications_service", function="deleteNotify")
        return 1


def getNotify(recipient):
    try:
        # Find recipient user
        recipient_user = User.query.filter_by(nickname=recipient).first()
        if not recipient_user:
            return 1  # Recipient not found

        # Query notifications with author and recipient nicknames
        AuthorUser = aliased(User)
        RecipientUser = aliased(User)

        notifications = db.session.query(
            Notification.id,
            AuthorUser.nickname.label("author_nickname"),
            RecipientUser.nickname.label("recipient_nickname"),
            Notification.title,
            Notification.content,
            Notification.type
        ).join(
            AuthorUser, AuthorUser.id == Notification.author_id
        ).join(
            RecipientUser, RecipientUser.id == Notification.recipient_id
        ).filter(
            Notification.recipient_id == recipient_user.id
        ).all()

        # Format results as list of dictionaries
        ntfs = [
            {
                "id": n.id,
                "author": n.author_nickname,
                "recipient": n.recipient_nickname,
                "title": n.title,
                "text": n.content,
                "type": n.type
            } for n in notifications
        ]

        return ntfs

    except Exception as e:
        elog(e, file="notifications_service", function="getNotify")
        return 1


def haveNotify(recipient):
    try:
        # Find recipient user
        recipient_user = User.query.filter_by(nickname=recipient).first()
        if not recipient_user:
            return -1  # Recipient not found

        # Query unread notifications
        unread_notifications = Notification.query.filter_by(
            recipient_id=recipient_user.id,
            is_read=False
        ).all()

        # Store results for return and debugging
        tmp = [(n.id, n.author_id, n.recipient_id, n.title, n.content, n.type, n.is_read)
               for n in unread_notifications]

        # Mark all notifications as read
        Notification.query.filter_by(recipient_id=recipient_user.id).update(
            {Notification.is_read: True}
        )

        # Commit changes
        db.session.commit()

        return bool(tmp)  # True if notifications exist, False if empty

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="notifications_service", function="haveNotify")
        return -1


def checkOffer(notificationId, librarianId):
    try:
        # Fetch notification by ID
        notification = Notification.query.get(notificationId)
        if not notification:
            return -1  # Notification not found

        # Check if the notification is an offer for this librarian
        if notification.type != "offer" or notification.recipient_id != librarianId:
            return -2  # Not a valid offer for this librarian

        return notification.author_id  # Return the author ID of the offer

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="notifications_service", function="checkOffer")
        return 1

    return 0