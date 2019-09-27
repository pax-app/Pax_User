from database import db
from project import create_app
from Flask import current_app


class User(db.Models):
    __tablename__ = 'USER'
