from database_singleton import Singleton
from project.api import bcrypt
from flask import current_app
import datetime
import jwt

db = Singleton().database_connection()


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
    def find(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

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
    rg_number = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('USER.user_id'))

    def __init__(self, minimum_price, maximum_price, bio, url_rg_photo, rg_number, user_id):
        self.minimum_price = minimum_price
        self.maximum_price = maximum_price
        self.bio = bio
        self.url_rg_photo = url_rg_photo
        self.rg_number = rg_number
        self.user_id = user_id

    def to_json(self):
        return{
            'provider_id': self.provider_id,
            'minimum_price': self.minimum_price,
            'maximum_price': self.maximum_price,
            'bio': self.bio,
            'url_rg_photo': self.url_rg_photo,
            'rg_number': self.rg_number,
            'user_id': self.user_id
        }

    @classmethod
    def find_provider(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class AddressModel(db.Model):
    __tablename__ = 'ADDRESS'

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    street = db.Column(db.String(30), nullable=False)
    neighborhood = db.Column(db.String(30), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    complement = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(20), nullable=False)
    cep = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(2), nullable=False)
    reference_point = db.Column(db.String(50), nullable=True)

    def __init__(self, street, neighborhood, number, complement, city, cep, state, reference_point):
        self.street = street
        self.neighborhood = neighborhood
        self.number = number
        self.complement = complement
        self.city = city
        self.cep = cep
        self.state = state
        self.reference_point = reference_point

    def to_json(self):
        return{
            'address_id': self.address_id,
            'street': self.street,
            'neighborhood': self.neighborhood,
            'number': self.number,
            'complement': self.complement,
            'city': self.city,
            'cep': self.cep,
            'state': self.state,
            'reference_point': self.reference_point
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class LivesModel(db.Model):
    __tablename__ = 'lives'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'USER.user_id'), primary_key=True, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey(
        'ADDRESS.address_id'), primary_key=True, nullable=False)

    def __init__(self, user_id, address_id):
        self.user_id = user_id
        self.address_id = address_id

    def to_json(self):
        return{
            'user_id': self.user_id,
            'address_id': self.address_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class WorksModel(db.Model):
    __tablename__ = 'works'

    provider_category_id = db.Column(
        db.Integer, nullable=False, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey(
        'PROVIDER.provider_id'), nullable=False, primary_key=True)

    def __init__(self, provider_category_id, provider_id):
        self.provider_category_id = provider_category_id
        self.provider_id = provider_id

    def to_json(self):
        return{
            'provider_category_id': self.provider_category_id,
            'provider_id': self.provider_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
