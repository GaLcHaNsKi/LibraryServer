import hashlib

from app.models import User
from app.views.logs import elog


SuccessResponse = ({"message": "Success"}, 200)
ForbiddenResponse = ({"error": "You cannot do this"}, 403)
BookNotFoundResponse = ({"error": "Book not found"}, 404)
LibraryNotFoundResponse = ({"error": "Library not found"}, 404)
UserNotFoundResponse = ({"error": "User not found"}, 404)
LibrarianAlreadyHiredResponse = ({"error": "Librarian already hired"}, 409)
LibrarianNotHiredResponse = ({"error": "You are not hired!"}, 403)
InternalErrorResponse = ({"error": "Internal Server Error"}, 500)


def hashPassword(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hex_dig = hash_object.hexdigest()

    return hex_dig


def getRole(nickname):
    try:
        # Query user by nickname
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            return -1
        return user.role.value  # Return the string value of the Role enum

    except Exception as e:
        elog(e, file="common_service", function="getRole")
        return -2


def isExists(nickname, coded_password=""):
    try:
        if coded_password:
            hashed_password = hashPassword(coded_password)
            user = User.query.filter_by(nickname=nickname, password_hash=hashed_password).first()

            if user:
                return user.id
        else:
            user = User.query.filter_by(nickname=nickname).first()

            if user:
                return user.id

    except Exception as e:
        elog(e, file="common_service", function="isExists")
        return -1

    return 0
