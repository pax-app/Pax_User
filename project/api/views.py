from __future__ import print_function  # In python 2.7
from flask import request, jsonify, Blueprint, abort, current_app
import sys
import json
from project.api.models import UserModel
from database import db, bcrypt
from project.api.utils import authenticate

users_blueprint = Blueprint('user', __name__)


def createFailMessage(message):
    response_object = {
        'status': 'fail',
        'message': '{}'.format(message)
    }
    return response_object


def createSuccessMessage(message):
    response_object = {
        'status': 'success',
        'message': '{}'.format(message)
    }
    return response_object

# User Registration Route
@users_blueprint.route('/auth/registration', methods=['POST'])
def user_registration():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(createFailMessage("Invalid Payload")), 400

    name = post_data["name"]
    email = post_data["email"]
    cpf = post_data["cpf"]
    password = post_data["password"]
    url_avatar = post_data["url_avatar"]
    user = UserModel(name, email, cpf, password, url_avatar)

    if UserModel.find_by_email(email):
        return jsonify(createFailMessage('{} already exists'.format(email))), 400

    try:
        user.save_to_db()
        auth_token = user.encode_auth_token(user.user_id)
        response_object = createSuccessMessage('User was created')
        response_object["auth_token"] = auth_token.decode()
        return jsonify(response_object), 201
    except:
        db.session.rollback()
        return jsonify(createFailMessage('Try again later')), 503
        # User Login Route


@users_blueprint.route('/auth/login', methods=['POST'])
def user_login():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(createFailMessage("Invalid Payload")), 400

    email = post_data["email"]
    password = post_data["password"]

    try:
        current_user = UserModel.find_by_email(email)

        if not current_user:
            return jsonify(createFailMessage('User {} doesn\'t exist'.format(email))), 404

        if current_user and bcrypt.check_password_hash(current_user.password, password):
            auth_token = current_user.encode_auth_token(current_user.user_id)
            response_object = createSuccessMessage('Successfully logged in.')
            response_object["auth_token"] = auth_token.decode()

            return jsonify(response_object), 200
        else:
            return jsonify(createFailMessage('Wrong Credentials')), 401
    except:
        return jsonify(createFailMessage("Try again")), 500

# Logout for access
@users_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def user_logout(resp):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return jsonify(response_object), 200


@users_blueprint.route('/auth/status', methods=['GET'])
@authenticate
def get_user_status(resp):
    user = UserModel.query.filter_by(user_id=resp).first()
    auth_token = user.encode_auth_token(user.user_id)
    response_object = {
        'status': 'success',
        'message': 'success',
        'data': user.to_json()
    }
    return jsonify(response_object), 200
