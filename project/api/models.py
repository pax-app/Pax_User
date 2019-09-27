<<<<<<< HEAD
from project import db


class UserModel(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoIncrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    url_avatar = db.Column(db.String(50), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
=======
from database import db
from project import create_app
from Flask import current_app


class User(db.Models):
    __tablename__ = 'USER'
>>>>>>> c52391a6923fdbde71b07842ffe08a455daf732f
