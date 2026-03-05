import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.views.logs import elog


SuccessResponse = ({"message": "Success"}, 200)
ForbiddenResponse = ({"error": "You cannot do this"}, 403)
BookNotFoundResponse = ({"error": "Book not found"}, 404)
LibraryNotFoundResponse = ({"error": "Library not found"}, 404)
UserNotFoundResponse = ({"error": "User not found"}, 404)
OfferNotFoundResponse = ({"error": "Offer not found"}, 404)
LibrarianAlreadyHiredResponse = ({"error": "Librarian already hired"}, 409)
LibrarianNotHiredResponse = ({"error": "You are not hired!"}, 403)
InternalErrorResponse = ({"error": "Internal Server Error"}, 500)


def hashPassword(password):
    return generate_password_hash(password)


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
        user = User.query.filter_by(nickname=nickname).first()

        if user:
            if coded_password:
                # Check backwards compatibility with sha256
                password_bytes = coded_password.encode('utf-8')
                hash_object = hashlib.sha256(password_bytes)
                hex_dig = hash_object.hexdigest()
                
                if user.password_hash == hex_dig:
                    # Update to new hashing transparently
                    user.password_hash = hashPassword(coded_password)
                    from app import db
                    db.session.commit()
                    return user.id
                elif check_password_hash(user.password_hash, coded_password):
                    return user.id
            else:
                return user.id

    except Exception as e:
        elog(e, file="common_service", function="isExists")
        return -1

    return 0
