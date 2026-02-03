from app.views.common_service import InternalErrorResponse, SuccessResponse
from app.views.library.places.places_service import addPlace, deletePlace, editPlace, getPlaceById, getPlaces
from flask import Blueprint, request
from app.views.library.places.shelves.shelves_routes import shelvesBlueprint

placesBlueprint = Blueprint("places", __name__)

placesBlueprint.register_blueprint(shelvesBlueprint, url_prefix="/<placeId>/shelves")

@placesBlueprint.route("/", methods=["GET"])
def sendPlacesListRoute():
    """
    ---
    tags:
        - places
    summary: List places
    responses:
            200:
                description: Places list
            500:
                description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]

    places_list = getPlaces(libraryId)

    if places_list == 1:
        return InternalErrorResponse

    return places_list

@placesBlueprint.route("/<placeId>", methods=["GET"])
def getPlaceRoute(placeId):
    """
    ---
    tags:
    - places
    summary: Get place by id
    parameters:
    - in: path
      name: placeId
      required: true
      type: integer
    responses:
      200:
        description: Place
      500:
        description: Internal Server Error
    """
    place = getPlaceById(placeId)

    if place == 1:
        return InternalErrorResponse

    return place

@placesBlueprint.route("/", methods=["POST"])
def addPlaceRoute():
    """
    ---
    tags:
    - places
    summary: Add place
    consumes:
    - application/x-www-form-urlencoded
    parameters:
      - in: formData
        name: name
        required: true
        type: string
      - in: formData
        name: description
        required: false
        type: string
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    libraryId = request.environ["user"]["libraryId"]

    place_name = request.form["name"]
    description = request.form.get("description")

    if addPlace(libraryId, place_name, description):
        return InternalErrorResponse

    return SuccessResponse

@placesBlueprint.route("/<placeId>", methods=["PUT"])
def editPlaceRoute(placeId):
    """
    ---
    tags:
    - places
    summary: Edit place
    consumes:
    - application/x-www-form-urlencoded
    parameters:
    - in: path
      name: placeId
      required: true
      type: integer
    - in: formData
      name: place_name
      required: false
      type: string
    - in: formData
      name: description
      required: false
      type: string
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    place_name = request.form.get("place_name")
    description = request.form.get("description")

    if editPlace(placeId, place_name, description):
        return InternalErrorResponse

    return SuccessResponse

@placesBlueprint.route("/<placeId>", methods=["DELETE"])
def deletePlaceRoute(placeId):
    """
    ---
    tags:
    - places
    summary: Delete place
    parameters:
    - in: path
      name: placeId
      required: true
      type: integer
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    if deletePlace(placeId):
        return InternalErrorResponse

    return SuccessResponse
