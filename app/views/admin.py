import hmac
import os
from datetime import datetime, time, timedelta
from functools import wraps

from flask import Blueprint, abort, current_app, make_response, redirect, render_template, request, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, select

from app import db
from app.models import Book, DevicePushToken, Library, OnHandsBook, Role, User


adminBlueprint = Blueprint("admin", __name__, url_prefix="/admin")

_ACCESS_COOKIE = "library_admin_access"
_ACCESS_TTL_SECONDS = 3 * 60 * 60
_TOKEN_SALT = "library-admin-access-v1"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_TOKEN_SALT)


def _has_valid_access_token():
    token = request.cookies.get(_ACCESS_COOKIE)
    if not token:
        return False
    try:
        payload = _serializer().loads(token, max_age=_ACCESS_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return False
    return payload == {"scope": "admin"}


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not _has_valid_access_token():
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped


def _count(model):
    return db.session.scalar(select(func.count()).select_from(model)) or 0


def _weekly_chart(date_column):
    today = datetime.utcnow().date()
    first_day = today - timedelta(days=6)
    first_moment = datetime.combine(first_day, time.min)
    timestamps = db.session.scalars(
        select(date_column).where(date_column >= first_moment)
    ).all()

    totals = {first_day + timedelta(days=offset): 0 for offset in range(7)}
    for timestamp in timestamps:
        if timestamp is not None and timestamp.date() in totals:
            totals[timestamp.date()] += 1

    highest = max(totals.values(), default=0) or 1
    points = []
    for index, (day, total) in enumerate(totals.items()):
        x = 50 + index * 100
        y = 184 - round(total / highest * 128)
        points.append({"x": x, "y": y, "label": day.strftime("%d.%m"), "count": total})

    return points, " ".join(f"{point['x']},{point['y']}" for point in points)


def _weekly_books_chart():
    today = datetime.utcnow().date()
    first_day = today - timedelta(days=6)
    first_moment = datetime.combine(first_day, time.min)
    books_by_day = {first_day + timedelta(days=offset): 0 for offset in range(7)}
    issued_by_day = books_by_day.copy()

    for created_at in db.session.scalars(select(Book.created_at).where(Book.created_at >= first_moment)):
        if created_at is not None and created_at.date() in books_by_day:
            books_by_day[created_at.date()] += 1
    for issued_at in db.session.scalars(select(OnHandsBook.issue_date).where(OnHandsBook.issue_date >= first_moment)):
        if issued_at is not None and issued_at.date() in issued_by_day:
            issued_by_day[issued_at.date()] += 1

    highest = max([*books_by_day.values(), *issued_by_day.values()], default=0) or 1
    points = []
    for index, day in enumerate(books_by_day):
        x = 50 + index * 100
        points.append({
            "x": x,
            "label": day.strftime("%d.%m"),
            "books": books_by_day[day],
            "books_y": 184 - round(books_by_day[day] / highest * 128),
            "issued": issued_by_day[day],
            "issued_y": 184 - round(issued_by_day[day] / highest * 128),
        })
    return points, " ".join(f"{point['x']},{point['books_y']}" for point in points), " ".join(
        f"{point['x']},{point['issued_y']}" for point in points
    )


@adminBlueprint.route("/login", methods=["GET", "POST"])
def login():
    configured_password = os.getenv("ADMIN_PASSWORD", "")
    configuration_missing = not configured_password or configured_password == "change-me"

    if _has_valid_access_token():
        return redirect(url_for("admin.dashboard"))

    error = None
    if request.method == "POST" and not configuration_missing:
        password = request.form.get("password", "")
        if hmac.compare_digest(password, configured_password):
            response = make_response(redirect(url_for("admin.dashboard")))
            response.set_cookie(
                _ACCESS_COOKIE,
                _serializer().dumps({"scope": "admin"}),
                max_age=_ACCESS_TTL_SECONDS,
                httponly=True,
                secure=current_app.config["REQUIRE_HTTPS"],
                samesite="Lax",
                path="/admin",
            )
            return response
        error = "Неверный пароль."

    status = 503 if configuration_missing else 200
    return render_template(
        "admin/login.html",
        title="Вход в админ-панель",
        configuration_missing=configuration_missing,
        error=error,
    ), status


@adminBlueprint.post("/logout")
@admin_required
def logout():
    response = make_response(redirect(url_for("admin.login")))
    response.delete_cookie(_ACCESS_COOKIE, path="/admin")
    return response


@adminBlueprint.route("/")
@admin_required
def dashboard():
    user_chart, user_chart_points = _weekly_chart(User.created_at)
    library_chart, library_chart_points = _weekly_chart(Library.created_at)
    book_chart, book_chart_points, issued_chart_points = _weekly_books_chart()
    role_counts = {
        role.value if role else "Не указана": count
        for role, count in db.session.execute(
            select(User.role, func.count(User.id)).group_by(User.role)
        ).all()
    }
    return render_template(
        "admin/dashboard.html",
        title="Обзор",
        users_count=_count(User),
        libraries_count=_count(Library),
        books_count=_count(Book),
        issued_books_count=_count(OnHandsBook),
        push_devices_count=_count(DevicePushToken),
        user_chart=user_chart,
        user_chart_points=user_chart_points,
        library_chart=library_chart,
        library_chart_points=library_chart_points,
        book_chart=book_chart,
        book_chart_points=book_chart_points,
        issued_chart_points=issued_chart_points,
        role_counts=role_counts,
        reader_count=role_counts.get(Role.READER.value, 0),
        librarian_count=role_counts.get(Role.LIBRARIAN.value, 0),
        owner_count=role_counts.get(Role.OWNER.value, 0),
    )


@adminBlueprint.route("/users")
@admin_required
def users():
    page_number = max(request.args.get("page", 1, type=int), 1)
    pagination = db.paginate(
        select(User).order_by(User.id.desc()),
        page=page_number,
        per_page=25,
        max_per_page=100,
        error_out=False,
    )
    return render_template(
        "admin/users.html",
        title="Пользователи",
        pagination=pagination,
    )
