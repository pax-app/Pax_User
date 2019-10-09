from database import db
from project.api import bcrypt
from flask import current_app
import datetime
import jwt


class UserModel(db.Model):
    __tablename__ = 'USER'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
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

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class ProviderModel(db.Model):
    __tablename__ = 'PROVIDER'

    provider_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    minimum_price = db.Column(db.Float)
    maximum_price = db.Column(db.Float)
    bio = db.Column(db.String(500), nullable=False)
    url_rg_photo = db.Column(db.String(50), nullable=False)
    issuing_organ = db.Column(db.String(10), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    number = db.Column(db.BigInteger)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'))

    def __init__(self, minimum_price, maximum_price, bio, url_rg_photo, issuing_organ, uf, number, user_id):
        self.minimum_price = minimum_price
        self.maximum_price = maximum_price
        self.bio = bio
        self.url_rg_photo = url_rg_photo
        self.issuing_organ = issuing_organ
        self.uf = uf
        self.number = number
        self.user_id = user_id
                                
    def to_json(self):
        return{
            'minimum_price': self.minimum_price,
            'maximum_price': self.maximum_price,
            'bio': self.bio,
            'url_rg_photo': self.url_rg_photo,
            'issuing_organ': self.issuing_organ,
            'uf': self.uf,
            'number': self.number,
            'user_id': self.user_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()