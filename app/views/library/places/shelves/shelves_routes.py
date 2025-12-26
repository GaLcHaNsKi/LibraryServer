from app.views.common_service import InternalErrorResponse, SuccessResponse
from app.views.library.places.shelves.shelves_service import getShelves, editShelf, addShelf, getShelveById, deleteShelf
from flask import Blueprint, request

shelvesBlueprint = Blueprint("shelves", __name__)

@shelvesBlueprint.route("/", methods=["GET"])
def sendShelvesList(placeId):
    """
    
    """
    
    libraryId = request.environ["user"]["libraryId"]

    shelves_list = getShelves(libraryId, placeId)

    if shelves_list == 1:
        return InternalErrorResponse

    return shelves_list

@shelvesBlueprint.route("/<shelveId>", methods=["GET"])
def getShelveById(shelveId):
    shelve = getShelveById(shelveId)

    if shelve == 1:
        return InternalErrorResponse

    return shelve

@shelvesBlueprint.route("/", methods=["DELETE"])
def deleteShelf(shelveId):
    if deleteShelf(shelveId):
        return InternalErrorResponse

    return SuccessResponse

@shelvesBlueprint.route("/", methods=["PUT"])
def editShelf(shelveId):
    shelf_name = request.form.get("shelf_name")
    description = request.form.get("description")

    if editShelf(shelveId, shelf_name, description):
        return InternalErrorResponse

    return SuccessResponse

@shelvesBlueprint.route("/", methods=["POST"])
def addShelf(placeId):
    libraryId = request.environ["user"]["libraryId"]

    shelf_name = request.form["shelf_name"]
    description = request.form.get("description")

    if addShelf(libraryId, placeId, shelf_name, description):
        return InternalErrorResponse

    return SuccessResponse
