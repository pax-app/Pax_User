from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()
bcrypt = Bcrypt()
