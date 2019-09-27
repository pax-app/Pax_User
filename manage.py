from __future__ import print_function  # In python 2.7
import sys
from project import create_app
from flask.cli import FlaskGroup
from flask import current_app
from database import db

# Config coverage report
app = create_app()
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()
