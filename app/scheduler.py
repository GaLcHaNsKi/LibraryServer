"""
Централизованный запуск фоновых задач (кронов) сервера.

Планировщик стартует автоматически при загрузке Flask-приложения
(см. app/__init__.py), поэтому кроны работают при ЛЮБОМ способе запуска:
- python run.py (socketio.run)
- flask run (в т.ч. с --debug)
- gunicorn / uwsgi
- WSGI (например, pythonanywhere)

Все новые кроны добавляются в start_schedulers() — единая точка регистрации.
"""
from apscheduler.schedulers.background import BackgroundScheduler

from app.crons.notification_cron import check_and_send_notifications

_scheduler = None


def start_schedulers():
    """Запускает все фоновые кроны. Идемпотентно: повторный вызов безопасен."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler()

    # Ежедневная проверка сроков возврата книг (каждый день в 00:00).
    # coalesce=True + большой misfire_grace_time: если сервер в 00:00 не
    # работал, пропущенный запуск будет выполнен сразу после старта,
    # а не потерян навсегда.
    _scheduler.add_job(
        func=check_and_send_notifications,
        trigger="cron",
        hour=0,
        minute=0,
        id="check_deadline_notifications",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=23 * 60 * 60,  # до 23 часов на «нагонку»
    )

    _scheduler.start()
    print("[Scheduler] фоновые кроны запущены")
    return _scheduler


def get_scheduler():
    """Возвращает активный планировщик (или None, если он не запущен)."""
    return _scheduler
