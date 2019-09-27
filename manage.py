from project import create_app
from flask.cli import FlaskGroup
from database import db
from flask import current_app

# Config coverage report
app = create_app()
cli = FlaskGroup(app)


app.config['SQLALCHEMY_DATABASE_URL'] = 'mysql://f15jto2ojbvbb18m:ojjbjm6lswedzs91@bqmayq5x95g1sgr9.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/j3uyakutbdjh3tdy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

db.init_app(app)

if __name__ == '__main__':
    cli()
