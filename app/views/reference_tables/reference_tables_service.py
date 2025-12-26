from app.models import db, BookGenre, DocumentType, BookCondition, Library, BibleBook
from app.views.logs import elog


def getGenres():
    try:
        genres = BookGenre.query.order_by(BookGenre.genre_name.asc()).all()
        return [
            {
                "id": g.id,
                "name": g.genre_name,
            }
            for g in genres
        ]
    except Exception as e:
        elog(e, file="reference_tables_service", function="getGenres")
        db.session.rollback()
        return 1


def getDocumentTypes():
    try:
        types = DocumentType.query.order_by(DocumentType.type_name.asc()).all()
        return [
            {
                "id": t.id,
                "name": t.type_name,
            }
            for t in types
        ]
    except Exception as e:
        elog(e, file="reference_tables_service", function="getDocumentTypes")
        db.session.rollback()
        return 1


def getConditions():
    try:
        conditions = (
            BookCondition.query
            .order_by(BookCondition.condition_name.asc())
            .all()
        )
        return [
            {
                "id": c.id,
                "name": c.condition_name
            }
            for c in conditions
        ]
    except Exception as e:
        elog(e, file="reference_tables_service", function="getConditions")
        db.session.rollback()
        return 1


def getBibleBooks():
    try:
        books = BibleBook.query.order_by(BibleBook.id.asc()).all()
        return [
            {
                "id": b.id,
                "ru": b.ru,
                "en": b.en,
            }
            for b in books
        ]
    except Exception as e:
        elog(e, file="reference_tables_service", function="getBibleBooks")
        db.session.rollback()
        return 1

