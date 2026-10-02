"""
Централизованный запуск фоновых задач (кронов) сервера.

Планировщик стартует автоматически при загрузке Flask-приложения
(см. app/__init__.py), поэтому кроны работают при ЛЮБОМ способе запуска:
- python run.py
- flask run (в т.ч. с --debug)
- gunicorn / uwsgi
- WSGI (например, pythonanywhere)

Все новые кроны добавляются в start_schedulers() — единая точка регистрации.
"""
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.crons.notification_cron import check_and_send_notifications

_scheduler = None


def start_schedulers():
    """Запускает все фоновые кроны. Идемпотентно: повторный вызов безопасен."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler()

    # Проверяем сроки сразу после запуска сервера и затем ежедневно в 08:00.
    # next_run_time нужен, потому что хранилище задач находится в памяти:
    # после полного перезапуска APScheduler сам не знает о пропущенном запуске.
    _scheduler.add_job(
        func=check_and_send_notifications,
        trigger="cron",
        hour=8,
        minute=0,
        id="check_deadline_notifications",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=23 * 60 * 60,  # до 23 часов на «нагонку»
        next_run_time=datetime.now() + timedelta(seconds=10),
    )

    _scheduler.start()
    print("[Scheduler] фоновые кроны запущены")
    return _scheduler


def get_scheduler():
    """Возвращает активный планировщик (или None, если он не запущен)."""
    return _scheduler
