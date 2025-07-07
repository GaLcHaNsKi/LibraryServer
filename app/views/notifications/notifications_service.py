from app import db
from app.models import User, Notification
from app.views.logs import elog


def sendNotify(author, recipient, title, content, type_):
    try:
        # Get author and recipient IDs
        author_user = User.query.filter_by(nickname=author).first()
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
        notifications = db.session.query(
            Notification.id,
            User.nickname.label("author_nickname"),
            User.nickname.label("recipient_nickname"),
            Notification.title,
            Notification.content,
            Notification.type
        ).join(
            User, User.id == Notification.author_id
        ).join(
            User, User.id == Notification.recipient_id, aliased=True
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
