from app import db
from app.models import User, Role, Director, Librarian, Library
from app.views.common_service import isExists
from app.views.logs import elog


def deleteUser(nickname):
    try:
        # Fetch user by nickname
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            return 1

        # Check if user is OWNER
        if user.role == Role.OWNER:
            return 2

        # Delete user
        db.session.delete(user)
        db.session.commit()

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, file="users_service", function="deleteUser")
        return 1

    return 0


def hireLibrarian(director_id, librarian):
    try:
        # Get library_id from director
        director = Director.query.filter_by(user_id=director_id).first()
        if not director:
            return 1  # Director not found

        lib_id = director.library_id

        # Get user_id of librarian by nickname
        user = User.query.filter_by(nickname=librarian).first()
        if not user:
            return 1  # Librarian user not found

        # Update librarian record
        librarian_record = Librarian.query.filter_by(user_id=user.id).first()
        if not librarian_record:
            return 1  # Librarian record not found

        librarian_record.director_id = director_id
        librarian_record.library_id = lib_id
        librarian_record.is_hired = True

        db.session.commit()

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, "users_service", "hireLibrarian")  # Assuming elog is defined
        return 1

    return 0


def dismissLibrarian(librarian):
    try:
        # Find user by nickname
        user = User.query.filter_by(nickname=librarian).first()
        if not user:
            return 1  # User not found

        # Find librarian record by user_id
        librarian_record = Librarian.query.filter_by(user_id=user.id).first()
        if not librarian_record:
            return 1  # Librarian record not found

        # Update librarian record
        librarian_record.director_id = None
        librarian_record.library_id = None
        librarian_record.is_hired = False

        # Commit changes
        db.session.commit()

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, "users_service", "dismissLibrarian")
        return 1

    return 0


def isHired(librarian):
    """
        Если librarian - библиотекарь, возвращаем:
            "" - не нанят;
            "library name" - название библиотеки, если нанят.
        Иначе если librarian - директор, возвращается название его библиотеки.
        Если такого нет, или произошла ошибка, возвращаем 1.
    """
    # Check if user exists
    if not isExists(librarian):
        return 1

    try:
        # Query user by nickname
        user = User.query.filter_by(nickname=librarian).first()
        if not user:
            return 1  # Shouldn't happen due to is_exists, but included for safety

        if user.role == Role.LIBRARIAN:
            # Query librarian with library join
            librarian_record = Librarian.query.filter_by(user_id=user.id).join(
                Library, Librarian.library_id == Library.id, isouter=True
            ).add_columns(Library.name).first()

            if not librarian_record or not librarian_record[1]:  # No library associated
                return ""
            return librarian_record[1]  # Library name

        elif user.role == Role.OWNER:
            # Query director with library join
            director_record = Director.query.filter_by(user_id=user.id).join(
                Library, Director.library_id == Library.id
            ).add_columns(Library.name).first()

            if not director_record or not director_record[1]:
                return 1  # Unexpected, but handle gracefully
            return director_record[1]  # Library name

        return 1  # Other roles (e.g., READER) are not handled

    except Exception as e:
        elog(e, "users_service", "isHired")
        return 1


def getUserIDByNickname(nickname):
    try:
        # Query user by nickname
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            return 0
        return user.id

    except Exception as e:
        elog(e, "users_service", "getUserIDByNickname")
        return 0


def getListOfLibrarians(director_id):
    code = 0
    lib_list = []
    try:
        # Query librarians joined with users, filter by director_id, order by nickname
        librarians = Librarian.query.join(User, User.id == Librarian.user_id)\
            .filter(Librarian.director_id == director_id)\
            .order_by(User.nickname.asc())\
            .add_columns(User.nickname).all()

        # Extract nicknames into list
        for librarian in librarians:
            lib_list.append(librarian[1])  # librarian[1] is the nickname

    except Exception as e:
        elog(e, "users_service", "getListOfLibrarians")
        code = 1

    return lib_list if code == 0 else 1


def getListOfDirectors():
    code = 0
    dir_list = []
    try:
        # Query users with OWNER role
        directors = User.query.filter_by(role=Role.OWNER).all()

        # Extract nicknames into list
        for user in directors:
            dir_list.append(user.nickname)

    except Exception as e:
        elog(e, "users_service", "getListOfDirectors")  # Assuming elog is defined
        code = 1

    return dir_list if code == 0 else 1
