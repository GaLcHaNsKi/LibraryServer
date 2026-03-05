from app import app, socketio
from apscheduler.schedulers.background import BackgroundScheduler
from app.crons.notification_cron import check_and_send_notifications

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_send_notifications, trigger="cron", hour=0, minute=0)
scheduler.start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
