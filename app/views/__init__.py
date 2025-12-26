from flask import render_template, send_file

from app import app, basedir
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.librarymiddleware import LibraryMiddleware
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

LASTEST_VERSION = "1-6"

app.wsgi_app = LibraryMiddleware(app.wsgi_app, app)
app.wsgi_app = AuthMiddleware(app.wsgi_app, app)

app.register_blueprint(authBlueprint, url_prefix="/auth")
app.register_blueprint(usersBlueprint, url_prefix="/users")
app.register_blueprint(notificationsBlueprint, url_prefix="/notifications")
app.register_blueprint(librariansBlueprint, url_prefix="/librarians")
app.register_blueprint(libraryBlueprint, url_prefix="/library")
app.register_blueprint(referencesBlueprint, url_prefix="/references")


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home", LASTEST_VERSION=LASTEST_VERSION)


@app.route("/guide")
def guide():
    return render_template("guide.html", title="Guide")


@app.route("/releases")
def releases():
    return render_template("releases.html", title="Releases")


@app.route("/releases/<apk>")
def download_apk(apk):
    file = basedir + f"/releases/{apk}"
    return send_file(file, download_name=apk, as_attachment=True)


@app.route("/robots.txt")
def robots():
    return send_file(
        basedir + "/robots.txt",
        mimetype="text/plain"
    )


@app.route("/sitemap.xml")
def sitemap():
    return send_file(
        basedir + "/sitemap.xml",
        mimetype="application/xml"
    )
