from app.views.logs import elog
from app import db
from app.models import Library, Director, Librarian, User, Role


def delLibraryByDirectorID(director_id):
    try:
        director = Director.query.filter_by(user_id=director_id).first()
        if not director or not director.library_id:
            return 0

        library = Library.query.filter_by(id=director.library_id).first()
        if not library:
            return 1  # Library not found

        lib_id = library.id
        Librarian.query.filter_by(library_id=lib_id).update({
            Librarian.is_hired: False,
            Librarian.director_id: None,
            Librarian.library_id: None
        })

        User.query.filter_by(id=director_id).update({
            User.role: Role.LIBRARIAN
        })

        Director.query.filter_by(user_id=director_id).delete()

        # Delete the library
        db.session.delete(library)

        # Commit all changes
        db.session.commit()
        return 0

    except Exception as e:
        db.session.rollback()
        elog(e, file="libraries_service", function="delLibraryByDirectorID")
        return 1


def transferLibrary(director_id, librarian_id):
    try:
        director = Director.query.filter_by(user_id=director_id).first()
        if not director or not director.library_id:
            return 2  # он не директор

        library = Library.query.filter_by(id=director.library_id).first()
        if not library:
            return 2  # он не директор этой библиотеки

        librarian = Librarian.query.filter_by(user_id=librarian_id, library_id=library.id).first()
        if not librarian:
            return 2  # пользователь не из этой библиотеки

        # Step 3: Update current director
        # - Set role=LIBRARIAN in User table
        User.query.filter_by(id=director_id).update({
            User.role: Role.LIBRARIAN
        })
        # - Create or update Librarian record for the former director
        existing_librarian = Librarian.query.filter_by(user_id=director_id).first()
        if existing_librarian:
            existing_librarian.is_hired = True
            existing_librarian.director_id = librarian_id
            existing_librarian.library_id = library.id
        else:
            new_librarian = Librarian(
                user_id=director_id,
                is_hired=True,
                director_id=librarian_id,
                library_id=library.id
            )
            db.session.add(new_librarian)
        # - Set Director.library_id to None
        director.library_id = None

        # Step 4: Update librarian to director
        # - Set role=OWNER in User table
        User.query.filter_by(id=librarian_id).update({
            User.role: Role.OWNER
        })
        # - Remove from Librarian table
        Librarian.query.filter_by(user_id=librarian_id).delete()
        # - Create or update Director record
        existing_director = Director.query.filter_by(user_id=librarian_id).first()
        if existing_director:
            existing_director.library_id = library.id
        else:
            new_director = Director(user_id=librarian_id, library_id=library.id)
            db.session.add(new_director)

        # Step 5: Update library to set new director
        library.director_id = librarian_id

        # Step 6: Update other librarians to point to new director
        Librarian.query.filter_by(director_id=director_id).update({
            Librarian.director_id: librarian_id
        })

        # Commit all changes
        db.session.commit()
        return 0

    except Exception as e:
        db.session.rollback()
        elog(e, file="libraries_service", function="transferLibrary")
        return 1
