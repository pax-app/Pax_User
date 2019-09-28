from __future__ import print_function  # In python 2.7
from flask import request, jsonify, Blueprint, abort
import sys
import json
from project.api.models import UserModel
from database import db, bcrypt

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
        return jsonify(createSuccessMessage('User {} was created'.format(name))), 200
    except:
        return jsonify(createFailMessage('DB out of reach')), 503
        # User Login Route


@users_blueprint.route('/auth/login', methods=['POST'])
def user_login():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(createFailMessage("Invalid Payload")), 400

    email = post_data["email"]
    password = post_data["password"]

    current_user = UserModel.find_by_email(email)

    if not current_user:
        return jsonify(createFailMessage('User {} doesn\'t exist'.format(email))), 400

    if current_user and bcrypt.check_password_hash(current_user.password, password):
        return jsonify(createSuccessMessage('Logged in as {}'.format(current_user.username))), 200
    else:
        return jsonify(createFailMessage('Wrong Credentials')), 401

# Logout for access
@users_blueprint.route('/auth/logout/access', methods=['POST'])
def user_logout_access():
    return jsonify({
        'message': 'logoutAccess'
    })

# Logout for Refresh Token
@users_blueprint.route('/auth/logout/refresh', methods=['POST'])
def user_logout_refresh():
    return jsonify({
        'message': 'logoutRefresh'
    })

# Token Refresh
@users_blueprint.route('/auth/token/refresh', methods=['POST'])
def user_token_refresh():
    return jsonify({
        'message': 'tokenRefresh'
    })

# secret endpoint (to test access with tokens)
@users_blueprint.route('/secret-resource', methods=['GET'])
def secret_resource():
    return jsonify({
        'answer': 42
    })
