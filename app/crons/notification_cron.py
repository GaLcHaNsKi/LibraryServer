import os
import sys
from datetime import datetime

# Обеспечиваем доступ к контексту приложения (так как скрипт запускается автономно)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app
from app.models import OnHandsBook, Book, NotificationSetting, Library, User, Librarian
from app.views.notifications.notifications_service import sendNotify


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

                should_notify = False
                is_before = False

                if days_diff > 0:
                    # Еще не просрочена
                    if days_diff <= setting.notify_before_days:
                        if days_diff == setting.notify_before_days or setting.is_every_day:
                            should_notify = True
                            is_before = True
                elif days_diff == 0:
                    # Последний день
                    should_notify = True  
                    is_before = True
                else:
                    # Просрочена
                    overdue = -days_diff
                    # Условие: если notify_after_days = 0, то значит после просрочки не напоминаем (настроено так). Либо напоминаем 1 раз на нужный день, либо каждый день после этого дня
                    if setting.notify_after_days > 0 and overdue >= setting.notify_after_days:
                        if overdue == setting.notify_after_days or setting.is_every_day:
                            should_notify = True
                            is_before = False

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
