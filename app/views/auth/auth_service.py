import hashlib

from app import db
from app.models import User, Role, Library, Librarian, Director
from app.views.common_service import hashPassword
from app.views.logs import elog


def addUser(nickname, coded_password, role, name="", description=""):
    try:
        # Check if nickname is already taken
        existing_user = User.query.filter_by(nickname=nickname).first()
        if existing_user:
            return "taken"

        # Hash the password
        hash_passw = hashPassword(coded_password)

        # Create new user
        new_user = User(
            nickname=nickname,
            password_hash=hash_passw,
            role=Role[role]
        )
        db.session.add(new_user)
        db.session.flush()  # Ensure user.id is available for foreign keys

        if role == "OWNER":
            # Create library
            new_library = Library(
                name=name,
                director_id=new_user.id,
                description=description
            )
            db.session.add(new_library)
            db.session.flush()  # Ensure library.id is available

            # Create director
            new_director = Director(
                user_id=new_user.id,
                library_id=new_library.id
            )
            db.session.add(new_director)
        elif role == "LIBRARIAN":
            # Create librarian
            new_librarian = Librarian(
                user_id=new_user.id
            )
            db.session.add(new_librarian)

        # Commit all changes
        db.session.commit()

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="users_control", function="add_user")  # Assuming elog is defined
        return "error"

    return 0
