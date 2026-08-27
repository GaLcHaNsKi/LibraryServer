from app import create_app
from app.models import db, User, Director, Librarian
from app.views.users.users_service import hireLibrarian

app = create_app()
with app.app_context():
    try:
        print("Creating test users...")
        u1 = User(nickname='dir1', password='p', email='e1', firstname='f', lastname='l', phone='1', role='owner')
        u2 = User(nickname='lib1', password='p', email='e2', firstname='f', lastname='l', phone='2', role='librarian')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        d = Director(user_id=u1.id)
        db.session.add(d)
        
        l = Librarian(user_id=u2.id)
        db.session.add(l)
        db.session.commit()
        
        print("Testing hireLibrarian...")
        res = hireLibrarian(u1.id, 'lib1')
        print("Result:", res)
        
    except Exception as e:
        print("Error:", e)
        db.session.rollback()
