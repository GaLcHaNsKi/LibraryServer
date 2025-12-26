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
    data = getGenres()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/document-types", methods=["GET"])
def document_types_list():
    data = getDocumentTypes()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/conditions", methods=["GET"])
def conditions_list():
    data = getConditions()
    if data == 1:
        return InternalErrorResponse
    return data


@referencesBlueprint.route("/bible-books", methods=["GET"])
def biblebooks_list():
    data = getBibleBooks()
    if data == 1:
        return InternalErrorResponse
    return data