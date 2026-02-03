from app.views.logs import elog
from app import db
from app.models import Library, Shelf

def getShelves(placeId: int) -> list[dict] | int:
    try:
        shelves = Shelf.query.filter_by(place_id=placeId).order_by(Shelf.shelve_name).all()

        return [
            {
                "id": shelf.id,
                "shelve_name": shelf.shelve_name
            } for shelf in shelves
        ]

    except Exception as e:
        elog(e, "shelve_service", "getShelves")
        return 1


def getShelveById(shelveId: int) -> dict | int:
    try:
        shelf = Shelf.query.filter_by(id=shelveId).first()
        if not shelf:
            return -1

        return {
            "id": shelf.id,
            "shelve_name": shelf.shelve_name,
            "description": shelf.description
        }

    except Exception as e:
        elog(e, "shelve_service", "getShelveById")
        return 1


def addShelf(placeId: int, shelf_name: str, description: str) -> int:
    try:
        shelf = Shelf(place_id=placeId, shelve_name=shelf_name, description=description)
        db.session.add(shelf)
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "shelve_service", "addShelf")
        return 1

def editShelf(shelveId: int, shelf_name: str, description: str) -> int:
    try:
        shelf = Shelf.query.filter_by(id=shelveId).first()
        if not shelf:
            return -1

        shelf.shelve_name = shelf_name
        shelf.description = description
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "shelve_service", "editShelf")
        return 1


def deleteShelf(shelveId: int) -> int:
    try:
        shelf = Shelf.query.filter_by(id=shelveId).first()
        if not shelf:
            return -1

        db.session.delete(shelf)
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "shelve_service", "deleteShelf")
        return 1