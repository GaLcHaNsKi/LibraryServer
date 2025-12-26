from app.views.logs import elog
from app import db
from app.models import Library, Shelf

def getShelves(library: str, placeId: int) -> list[dict] | int:
    try:
        lib = Library.query.filter_by(name=library).first()
        if not lib:
            return -1

        shelves = Shelf.query.filter_by(place_id=placeId).order_by(Shelf.shelve_name).all()

        return [
            {
                "id": shelf.id,
                "shelve_name": shelf.shelve_name,
                "description": shelf.description
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


def addShelf(library: str, placeId: int, shelf_name: str, description: str) -> int:
    try:
        lib = Library.query.filter_by(name=library).first()
        if not lib:
            return -1

        shelf = Shelf(place_id=placeId, shelve_name=shelf_name, description=description)
        db.session.add(shelf)
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
        return 0

    except Exception as e:
        elog(e, "shelve_service", "deleteShelf")
        return 1