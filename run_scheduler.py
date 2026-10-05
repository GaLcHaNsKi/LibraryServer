"""Runs the deadline-notification scheduler as one dedicated process."""
from app.scheduler import start_schedulers


if __name__ == "__main__":
    start_schedulers()
