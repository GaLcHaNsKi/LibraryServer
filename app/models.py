from app import db

OWNER = 1
LIBRARIAN = 0
ADMIN = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key=1)
    nickname = db.Column(db.String(50), unique=1)
    coded_password = db.Column(db.String(20))
    role = db.Column(db.Integer)
    hired = db.Column(db.Boolean)
    director = db.Column(db.String(50))

    def __repr__(self):
        return "User: " + self.nickname + "\nRole: " + "Owner" if self.role == 1 else "Librarian" if self.role == 0 else "Admin"

"""class Notifications(db.Model):
    author = db.Column(db.String(50))
    recipient = db.Column(db.String(50))
    title = db.Column(db.String(50))
    text = db.Column(db.String(100))

    def __repr__(self):
        return self.title + "\n" + self.text"""
#notifications = db.Table("notifications", )