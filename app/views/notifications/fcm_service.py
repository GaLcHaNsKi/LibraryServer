"""Best-effort Firebase Cloud Messaging delivery.

Notifications are always saved to the database first. FCM is an additional
delivery channel and must never make the primary notification operation fail.
"""
import os

from app import db
from app.models import DevicePushToken
from app.views.logs import elog


_firebase_app = None
_firebase_disabled = False


def _get_firebase_app():
    global _firebase_app, _firebase_disabled
    if _firebase_app is not None:
        return _firebase_app
    if _firebase_disabled:
        return None

    service_account_file = os.getenv('FCM_SERVICE_ACCOUNT_FILE')
    if not service_account_file:
        _firebase_disabled = True
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        _firebase_app = firebase_admin.initialize_app(
            credentials.Certificate(service_account_file)
        )
        return _firebase_app
    except Exception as e:
        _firebase_disabled = True
        elog(e, file='fcm_service', function='_get_firebase_app')
        return None


def send_fcm_notification(recipient_id: int, notification_id: int, author: str,
                          title: str, content: str, notification_type: str):
    """Sends a high-priority data message to all of a user's registered devices."""
    app = _get_firebase_app()
    if not app:
        return

    tokens = DevicePushToken.query.filter_by(user_id=recipient_id, platform='android').all()
    if not tokens:
        return

    try:
        from firebase_admin import messaging

        messages = [
            messaging.Message(
                data={
                    'notification_id': str(notification_id),
                    'author': author or '',
                    'title': title or '',
                    'text': content or '',
                    'type': notification_type or 'message',
                },
                token=device.token,
                android=messaging.AndroidConfig(priority='high'),
            )
            for device in tokens
        ]
        response = messaging.send_each(messages, app=app)
        invalid_tokens = [
            device.token for device, result in zip(tokens, response.responses)
            if not result.success and getattr(result.exception, 'code', None) in {
                'registration-token-not-registered', 'invalid-argument'
            }
        ]
        if invalid_tokens:
            DevicePushToken.query.filter(DevicePushToken.token.in_(invalid_tokens)).delete(
                synchronize_session=False
            )
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        elog(e, file='fcm_service', function='send_fcm_notification')
