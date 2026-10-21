from flask import abort, redirect, render_template, send_file, send_from_directory, url_for
from pathlib import Path

from app import app, basedir
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.librarymiddleware import LibraryMiddleware
from app.middleware.security_middleware import SecurityMiddleware
from app.views.auth import authBlueprint
from app.views.librarians import librariansBlueprint
from app.views.library import libraryBlueprint
from app.views.notifications import notificationsBlueprint
from app.views.users import usersBlueprint
from app.views.reference_tables import referencesBlueprint

"""
    Возвращаемые значения:
        0 - всё хорошо;
        1 - такого нет среди пользователей (или пароль не тот);
        2 - библиотекарь нанят;
        3 - nickname занят;
        4 - библиотекарь не нанят;
        5 - неизвестная команда;
        6 - ошибка базы данных;
        7 - книг больше нет;
        8 - некоторая ошибка;
        9 - нельзя удалить директора/библиотеку;
        10 - левый пользователь;
        11 - ожидается дата

    Значения параметра cmd:
        "send" - отправить оповещение;
        "read" - прочитал оповещение, удалить;
        "offer" - пригласить на работу;
        "hire" - нанять библиотекаря;
        "dismiss" - уволить бибилиотекаря;
"""

LATEST_VERSION = "2-0"
LATEST_VERSION_LABEL = "2.0"

DOC_PAGES = {
    "start": ("Начало работы", "docs/start.html"),
    "catalog": ("Каталог и поиск", "docs/catalog.html"),
    "lending": ("Выдача книг", "docs/lending.html"),
    "team": ("Библиотекари", "docs/team.html"),
    "settings": ("Настройки", "docs/settings.html"),
}

# Security is outermost so unauthenticated requests cannot send credentials or
# large payloads over HTTP before the checks run.
app.wsgi_app = LibraryMiddleware(app.wsgi_app, app)
app.wsgi_app = AuthMiddleware(app.wsgi_app, app)
app.wsgi_app = SecurityMiddleware(app.wsgi_app, app)

app.register_blueprint(authBlueprint, url_prefix="/auth")
app.register_blueprint(usersBlueprint, url_prefix="/users")
app.register_blueprint(notificationsBlueprint, url_prefix="/notifications")
app.register_blueprint(librariansBlueprint, url_prefix="/librarians")
app.register_blueprint(libraryBlueprint, url_prefix="/library")
app.register_blueprint(referencesBlueprint, url_prefix="/references")


@app.route("/")
@app.route("/index")
def index():
    """
    ---
    tags:
    - public
    summary: Home page
    responses:
      200:
        description: HTML page
    security: []
    """
    return render_template(
        "index.html",
        title="Главная",
        description="Library — Android-приложение для каталога и выдачи книг в домашней или небольшой библиотеке.",
    )


@app.route("/guide")
def guide():
    """
    ---
    tags:
    - public
    summary: Guide page
    responses:
      200:
        description: HTML page
    security: []
    """
    return redirect(url_for("docs_index"), code=301)


@app.route("/docs")
def docs_index():
    return render_template(
        "docs/index.html",
        title="Документация 2.0",
        description="Документация по использованию приложения Library 2.0.",
        doc_page="index",
    )


@app.route("/docs/2.0/<page>")
def docs_page(page):
    doc = DOC_PAGES.get(page)
    if doc is None:
        abort(404)
    title, template = doc
    return render_template(
        template,
        title=f"{title} — документация 2.0",
        description=f"{title}: руководство по приложению Library 2.0.",
        doc_page=page,
    )


@app.route("/site-map")
def site_map():
    return render_template(
        "site_map.html",
        title="Карта сайта",
        description="Карта сайта Library: приложение, загрузка и документация.",
    )


@app.route("/releases")
def releases():
    """
    ---
    tags:
    - public
    summary: Releases page
    responses:
      200:
        description: HTML page
    security: []
    """
    return render_template(
        "releases.html",
        title="Скачать",
        description="Скачать APK приложения Library для Android.",
        latest_version=LATEST_VERSION,
        latest_version_label=LATEST_VERSION_LABEL,
    )


@app.route("/releases/<apk>")
def download_apk(apk):
    """
    ---
    tags:
    - public
    summary: Download APK
    parameters:
    - in: path
      name: apk
      required: true
      type: string
    responses:
      200:
        description: File download
    security: []
    """
    # Do not turn a URL segment into an arbitrary filesystem path.
    releases_dir = Path(basedir) / "releases"
    if Path(apk).name != apk or not apk.endswith(".apk") or not (releases_dir / apk).is_file():
        abort(404)
    return send_from_directory(releases_dir, apk, as_attachment=True, download_name=apk)


@app.route("/robots.txt")
def robots():
    """
    ---
    tags:
    - public
    summary: Robots.txt
    responses:
      200:
        description: Text file
    security: []
    """
    return send_file(
        basedir + "/robots.txt",
        mimetype="text/plain"
    )


@app.route("/sitemap.xml")
def sitemap():
    """
    ---
    tags:
    - public
    summary: Sitemap
    responses:
      200:
        description: XML file
    security: []
    """
    pages = [
        url_for("index", _external=True),
        url_for("releases", _external=True),
        url_for("docs_index", _external=True),
        *(url_for("docs_page", page=page, _external=True) for page in DOC_PAGES),
        url_for("site_map", _external=True),
    ]
    return (
        render_template(
            "sitemap.xml",
            pages=pages,
            last_modified="2026-10-06",
        ),
        200,
        {"Content-Type": "application/xml; charset=utf-8"},
    )
