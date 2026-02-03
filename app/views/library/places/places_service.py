from app.views.logs import elog
from app import db
from app.models import Place

def getPlaces(libraryId: int) -> list[dict] | int:
    """
        Возвращает отсортированный список уникальных мест хранения книг
    """
    try:
        locations = Place.query.filter_by(library_id=libraryId).order_by(Place.place_name).all()

        return [
            {
                "id": location.id,
                "name": location.place_name
            } for location in locations
        ]

    except Exception as e:
        elog(e, "library_service", "getPlaces")
        return 1


def getPlaceById(placeId: int) -> dict | int:
    try:
        place = Place.query.filter_by(id=placeId).first()
        if not place:
            return -1

        return {
            "id": place.id,
            "name": place.place_name,
            "description": place.description
        }

    except Exception as e:
        elog(e, "library_service", "getPlaceById")
        return 1
    
def addPlace(libraryId: int, place_name: str, description: str) -> int:
    try:
        place = Place(place_name=place_name, description=description, library_id=libraryId)
        db.session.add(place)
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "library_service", "addPlace")
        return 1

def editPlace(placeId: int, place_name: str, description: str) -> int:
    try:
        place = Place.query.filter_by(id=placeId).first()
        if not place:
            return -1

        if place_name:
            place.place_name = place_name
        if description:
            place.description = description
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "library_service", "editPlace")
        return 1

def deletePlace(placeId: int) -> int:
    try:
        place = Place.query.filter_by(id=placeId).first()
        if not place:
            return -1

        db.session.delete(place)
        db.session.commit()
        return 0

    except Exception as e:
        elog(e, "library_service", "deletePlace")
        return 1
