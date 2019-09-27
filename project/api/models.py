from database import db, bcrypt
from flask import current_app
import datetime


class UserModel(db.Model):
    __tablename__ = 'USER'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    url_avatar = db.Column(db.String(50), nullable=False)

    def __init__(self, name, email, cpf, password, url_avatar):
        self.name = name
        self.email = email
        self.cpf = cpf
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.url_avatar = url_avatar

    def to_json(self):
        return{
            'name': self.name,
            'email': self.email,
            'cpf': self.cpf,
            'password': self.password,
            'url_avatar': self.url_avatar
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
