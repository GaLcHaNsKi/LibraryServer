from app import db
from app.models import Notification, User, Role, Director, Librarian, Library
from app.views.common_service import isExists
from app.views.logs import elog


def getUserInfo(userId):
    """
    Возвращает информацию о пользователе: имя, роль, нанят ли, название библиотеки.
    """
    try:
        user = User.query.filter_by(id=userId).first()
        if not user:
            return -1

        result = {
            "nickname": user.nickname,
            "email": user.email,
            "role": user.role.value,
        }

        if user.role == Role.LIBRARIAN:
            librarian = Librarian.query.filter_by(user_id=user.id).first()
            if librarian:
                result["is_hired"] = librarian.is_hired
                if librarian.is_hired and librarian.library_id:
                    library = Library.query.filter_by(id=librarian.library_id).first()
                    result["library"] = library.name if library else None
                else:
                    result["library"] = None
            else:
                result["is_hired"] = False
                result["library"] = None

        elif user.role == Role.OWNER:
            director = Director.query.filter_by(user_id=user.id).first()
            if director and director.library_id:
                library = Library.query.filter_by(id=director.library_id).first()
                result["library"] = library.name if library else None
            else:
                result["library"] = None

        return result

    except Exception as e:
        elog(e, file="users_service", function="getUserInfo")
        return 1


def editUser(userId, newNickname, newEmail):
    """Atomically updates the current user's nickname and email."""
    try:
        user = User.query.filter_by(id=userId).first()
        if not user:
            return -1

        existing = User.query.filter_by(nickname=newNickname).first()
        if existing and existing.id != user.id:
            return -2

        new_email = newEmail.strip() if newEmail else None
        if new_email:
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != user.id:
                return -3

        user.nickname = newNickname
        user.email = new_email
        db.session.commit()
        return 0

    except Exception as e:
        db.session.rollback()
        elog(e, file="users_service", function="editUser")
        return 1


def acceptOffer(librarian_id: int, notification_id: int):
    """Hires a librarian and consumes the accepted offer in one transaction."""
    try:
        offer = Notification.query.filter_by(
            id=notification_id, recipient_id=librarian_id, type="offer"
        ).with_for_update().first()
        if not offer:
            return -1, None

        librarian = Librarian.query.filter_by(user_id=librarian_id).with_for_update().first()
        if not librarian:
            return -2, None
        if librarian.is_hired:
            return -3, None

        director = Director.query.filter_by(user_id=offer.author_id).first()
        if not director or not director.library_id:
            return -2, None

        librarian.director_id = offer.author_id
        librarian.library_id = director.library_id
        librarian.is_hired = True
        db.session.delete(offer)
        db.session.commit()
        return 0, offer.author_id
    except Exception as e:
        db.session.rollback()
        elog(e, "users_service", "acceptOffer")
        return 1, None


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


def dismissLibrarian(director_id, librarian):
    try:
        d = Director.query.filter_by(user_id=director_id).first()
        
        if not d:
            return -1  # it is not director
        
        # Find user by nickname
        user = User.query.filter_by(nickname=librarian).first()
        if not user:
            return 1  # User not found

        # Find librarian record by user_id
        librarian_record = Librarian.query.filter_by(user_id=user.id, director_id=director_id).first()
        if not librarian_record:
            return 2  # Librarian record not found

        # Update librarian record
        librarian_record.director_id = None
        librarian_record.library_id = None
        librarian_record.is_hired = False

        # Commit changes
        db.session.commit()

    except Exception as e:
        db.session.rollback()  # Roll back on error
        elog(e, "users_service", "dismissLibrarian")
        return -2

    return 0


def selfDismissLibrarian(user_id):
    """
    Библиотекарь увольняется сам: снимает привязку к директору и библиотеке.
    Возвращает:
        0  - успешно;
        -1 - пользователь не найден;
        -3 - это не библиотекарь;
        -4 - библиотекарь не нанят;
        -2 - ошибка БД.
    """
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return -1

        if user.role != Role.LIBRARIAN:
            return -3

        librarian_record = Librarian.query.filter_by(user_id=user_id).first()
        if not librarian_record:
            return -1

        if not librarian_record.is_hired:
            return -4

        # Запоминаем директора, чтобы уведомить его после увольнения
        director_id = librarian_record.director_id

        # Снимаем наём
        librarian_record.director_id = None
        librarian_record.library_id = None
        librarian_record.is_hired = False

        db.session.commit()

        # Уведомляем директора, что библиотекарь уволился сам.
        # Импорт локальный — чтобы не создавать циклическую зависимость
        # между модулями users_service и notifications_service.
        if director_id and User.query.get(director_id):
            from app.views.notifications.notifications_service import sendNotify
            sendNotify(
                user.nickname,
                director_id,
                "Библиотекарь уволился",
                f"{user.nickname} уволился из вашей библиотеки.",
                "message"
            )

        return 0

    except Exception as e:
        db.session.rollback()
        elog(e, "users_service", "selfDismissLibrarian")
        return -2


def isHired(librarian):
    """
        Если librarian - библиотекарь, возвращаем:
            "" - не нанят;
            "library name" - название библиотеки, если нанят.
        Иначе если librarian - директор, возвращается название его библиотеки.
        Если такого нет, или произошла ошибка, возвращаем 1 и 2, соответственно.
    """

    try:
        user = User.query.filter_by(nickname=librarian).first()

        if not user:
            return 1

        if user.role == Role.LIBRARIAN:
            library_name = db.session.query(Library.name).select_from(Librarian).join(Library, isouter=True).filter(Librarian.user_id == user.id).scalar()
            return library_name if library_name else ""

        elif user.role == Role.OWNER:
            library_name = db.session.query(Library.name).select_from(Director).join(Library).filter(Director.user_id == user.id).scalar()
            return library_name if library_name else ""

        return ""  # User is neither librarian nor owner

    except Exception as e:
        elog(e, "users_service", "isHired")
        return 2


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
