from app.views.common_service import InternalErrorResponse, SuccessResponse
from app.views.library.places.shelves.shelves_service import getShelves, editShelf, addShelf, getShelveById, deleteShelf
from flask import Blueprint, request

shelvesBlueprint = Blueprint("shelves", __name__)

@shelvesBlueprint.route("/", methods=["GET"])
def sendShelvesListRoute(placeId):
    """
    ---
    tags:
    - shelves
    summary: List shelves for place
    parameters:
    - in: path
      name: placeId
      required: true
      type: integer
    responses:
      200:
        description: Shelves list
      500:
        description: Internal Server Error
    """
    shelves_list = getShelves(int(placeId))

    if shelves_list == 1:
        return InternalErrorResponse

    return shelves_list

@shelvesBlueprint.route("/<shelveId>", methods=["GET"])
def getShelveByIdRoute(shelveId):
    """
    ---
    tags:
    - shelves
    summary: Get shelf by id
    parameters:
    - in: path
      name: shelveId
      required: true
      type: integer
    responses:
      200:
        description: Shelf
      500:
        description: Internal Server Error
    """
    shelve = getShelveById(shelveId)

    if shelve == 1:
        return InternalErrorResponse

    return shelve

@shelvesBlueprint.route("/<shelveId>", methods=["DELETE"])
def deleteShelfRoute(shelveId):
    """
    ---
    tags:
    - shelves
    summary: Delete shelf
    parameters:
    - in: path
      name: shelveId
      required: true
      type: integer
    responses:
      200:
        description: Success
      500:
        description: Internal Server Error
    """
    if deleteShelf(shelveId):
        return InternalErrorResponse

    return SuccessResponse

@shelvesBlueprint.route("/<shelveId>", methods=["PUT"])
def editShelfRoute(shelveId):
    """
    ---
    tags:
    - shelves
    summary: Edit shelf
    consumes:
    - application/x-www-form-urlencoded
    parameters:
    - in: path
      name: shelveId
      required: true
      type: integer
    - in: formData
      name: shelf_name
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
    shelf_name = request.form.get("shelf_name")
    description = request.form.get("description")

    if editShelf(shelveId, shelf_name, description):
        return InternalErrorResponse

    return SuccessResponse

@shelvesBlueprint.route("/", methods=["POST"])
def addShelfRoute(placeId):
    """
    ---
    tags:
    - shelves
    summary: Add shelf
    consumes:
    - application/x-www-form-urlencoded
    parameters:
    - in: path
      name: placeId
      required: true
      type: integer
    - in: formData
      name: shelf_name
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
    shelf_name = request.form["shelf_name"]
    description = request.form.get("description")

    if addShelf(int(placeId), shelf_name, description):
        return InternalErrorResponse

    return SuccessResponse
