from app.views.common_service import InternalErrorResponse
from app.views.library.places.places_service import getPlaces
from flask import Blueprint, request
from app.views.library.places.shelves.shelves_routes import shelvesBlueprint

placesBlueprint = Blueprint("places", __name__)

placesBlueprint.register_blueprint(shelvesBlueprint, url_prefix="/<placeId>/shelves")

@placesBlueprint.route("/", methods=["GET"])
def sendPlacesList():
    libraryId = request.environ["user"]["libraryId"]

    places_list = getPlaces(libraryId)

    if places_list == 1:
        return InternalErrorResponse

    return places_list

@placesBlueprint.route("/<placeId>", methods=["GET"])
def getPlace(placeId):
    place = getPlaceById(placeId)

    if place == 1:
        return InternalErrorResponse

    return place

@placesBlueprint.route("/", methods=["POST"])
def addPlace():
    libraryId = request.environ["user"]["libraryId"]

    place_name = request.form["place_name"]
    description = request.form.get("description")

    if addPlace(libraryId, place_name, description):
        return InternalErrorResponse

    return SuccessResponse

@placesBlueprint.route("/<placeId>", methods=["PUT"])
def editPlace(placeId):
    place_name = request.form.get("place_name")
    description = request.form.get("description")

    if editPlace(placeId, place_name, description):
        return InternalErrorResponse

    return SuccessResponse

@placesBlueprint.route("/<placeId>", methods=["DELETE"])
def deletePlace(placeId):
    if deletePlace(placeId):
        return InternalErrorResponse

    return SuccessResponse
