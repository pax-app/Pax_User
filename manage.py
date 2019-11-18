from project import create_app
from flask.cli import FlaskGroup

# Config coverage report
app = create_app()
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()
