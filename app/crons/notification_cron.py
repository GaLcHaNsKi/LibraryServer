from datetime import datetime

from app import app
from app.models import OnHandsBook, Book, NotificationSetting, Library, User, Librarian
from app.views.notifications.notifications_service import sendNotify


def _notification_state(days_diff, notify_before_days, notify_after_days, is_every_day):
    """Возвращает (нужно_уведомить, срок_ещё_не_прошёл)."""
    before_days = max(notify_before_days or 0, 0)
    after_days = max(notify_after_days or 0, 0)
    every_day = bool(is_every_day)

    if days_diff > 0:
        should_notify = days_diff <= before_days and (days_diff == before_days or every_day)
        return should_notify, should_notify
    if days_diff == 0:
        return True, True

    overdue = -days_diff
    should_notify = after_days > 0 and overdue <= after_days and (overdue == after_days or every_day)
    return should_notify, False


def check_and_send_notifications():
    print(f"Running notification cron at {datetime.now()}")
    with app.app_context():
        # Получаем все выданные книги
        on_hands = OnHandsBook.query.all()
        today = datetime.now().date()

        for oh_book in on_hands:
            if not oh_book.return_date:
                continue

            book = Book.query.get(oh_book.book_id)
            if not book:
                continue
                
            library = Library.query.get(book.library_id)
            if not library:
                continue

            return_date = oh_book.return_date.date()
            days_diff = (return_date - today).days

            # Собираем всех потенциальных получателей: читатель, библиотекари, директор
            recipients_ids = []
            if oh_book.recipient_id:
                recipients_ids.append((oh_book.recipient_id, "reader"))
                
            librarians = Librarian.query.filter_by(library_id=library.id, is_hired=True).all()
            for lib in librarians:
                recipients_ids.append((lib.user_id, "staff"))
            
            if library.director_id:
                recipients_ids.append((library.director_id, "staff"))

            # Убираем дубликаты
            unique_recipients = {}
            for r_id, r_type in recipients_ids:
                # Если уже есть как reader, staff не перетирает, и наоборот
                if r_id not in unique_recipients or unique_recipients[r_id] == "staff":
                    unique_recipients[r_id] = r_type

            # Проверяем для каждого пользователя его персональные настройки
            for user_id, role_type in unique_recipients.items():
                setting = NotificationSetting.query.filter_by(user_id=user_id).first()
                if not setting:
                    setting = NotificationSetting(
                        notify_before_days=1,
                        notify_after_days=0,
                        is_every_day=False
                    )

                should_notify, is_before = _notification_state(
                    days_diff,
                    setting.notify_before_days,
                    setting.notify_after_days,
                    setting.is_every_day,
                )

                if should_notify:
                    _send_personal_notification(user_id, role_type, library, book, oh_book, days_diff, is_before)


def _send_personal_notification(user_id, role_type, library, book, oh_book, days_diff, is_before):
    director = User.query.get(library.director_id)
    author_nickname = director.nickname if director else "Система"
    
    recipient = User.query.get(user_id)
    if not recipient:
        return

    # Формируем текст в зависимости от того, читатель это или сотрудник
    if is_before:
        if days_diff > 0:
            title = "Напоминание о возврате книги"
            if role_type == "reader":
                text = f"Напоминаем, что вам нужно вернуть книгу '{book.title_ru}' (Инв. № {book.inventory_num}) через {days_diff} дней."
            else:
                text = f"У читателя {oh_book.recipient_name} подходит срок возврата книги '{book.title_ru}' (через {days_diff} дней)."
        else:
            title = "Сегодня срок возврата книги!"
            if role_type == "reader":
                text = f"Сегодня вам нужно вернуть книгу '{book.title_ru}' (Инв. № {book.inventory_num})."
            else:
                text = f"У читателя {oh_book.recipient_name} сегодня срок возврата книги '{book.title_ru}'."
    else:
        overdue = -days_diff
        title = "Просрочка возврата книги!"
        if role_type == "reader":
            text = f"Вы просрочили возврат книги '{book.title_ru}' (Инв. № {book.inventory_num}) на {overdue} дней."
        else:
            text = f"Читатель {oh_book.recipient_name} просрочил книгу '{book.title_ru}' (Инв. № {book.inventory_num}) на {overdue} дней."

    sendNotify(author_nickname, recipient.nickname, title, text, "warning")

if __name__ == "__main__":
    check_and_send_notifications()
