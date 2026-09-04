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
    libraryId = request.environ["user"]["libraryId"]
    shelves_list = getShelves(libraryId, int(placeId))

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
    libraryId = request.environ["user"]["libraryId"]
    shelve = getShelveById(libraryId, shelveId)

    if shelve == 1:
        return InternalErrorResponse
    if shelve == -1:
        return {"error": "Shelf not found"}, 404

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
    libraryId = request.environ["user"]["libraryId"]
    code = deleteShelf(libraryId, shelveId)
    if code == -1:
        return {"error": "Shelf not found"}, 404
    if code:
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
    libraryId = request.environ["user"]["libraryId"]
    shelf_name = request.form.get("shelf_name")
    description = request.form.get("description")

    code = editShelf(libraryId, shelveId, shelf_name, description)
    if code == -1:
        return {"error": "Shelf not found"}, 404
    if code == 2:
        return {"error": "Shelf name is required"}, 400
    if code == 3:
        return {"error": "Shelf name already exists"}, 409
    if code:
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
    libraryId = request.environ["user"]["libraryId"]
    shelf_name = request.form["shelf_name"]
    description = request.form.get("description")

    code = addShelf(libraryId, int(placeId), shelf_name, description)
    if code == -1:
        return {"error": "Place not found"}, 404
    if code == 2:
        return {"error": "Shelf name is required"}, 400
    if code == 3:
        return {"error": "Shelf name already exists"}, 409
    if code:
        return InternalErrorResponse

    return SuccessResponse
