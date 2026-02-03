# /references/
#             genres
#             document-types
#             conditions
#             bible-books

from flask import Blueprint, request

from app.views.common_service import InternalErrorResponse
from app.views.reference_tables.reference_tables_service import (
    getGenres,
    getDocumentTypes,
    getConditions,
    getBibleBooks,
)


referencesBlueprint = Blueprint("references", __name__)


@referencesBlueprint.route("/genres", methods=["GET"])
def genres_list():
    """
    ---
    tags:
        - reference-tables
    summary: List book genres
    responses:
            200:
                description: Genres list
            500:
                description: Internal Server Error
    """
    data = getGenres()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/document-types", methods=["GET"])
def document_types_list():
    """
    ---
    tags:
        - reference-tables
    summary: List document types
    responses:
            200:
                description: Document types list
            500:
                description: Internal Server Error
    """
    data = getDocumentTypes()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/conditions", methods=["GET"])
def conditions_list():
    """
    ---
    tags:
        - reference-tables
    summary: List book conditions
    responses:
            200:
                description: Conditions list
            500:
                description: Internal Server Error
    """
    data = getConditions()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/bible-books", methods=["GET"])
def biblebooks_list():
    """
    ---
    tags:
        - reference-tables
    summary: List bible books
    responses:
            200:
                description: Bible books list
            500:
                description: Internal Server Error
    """
    data = getBibleBooks()
    if data == 1:
        return InternalErrorResponse
    return data