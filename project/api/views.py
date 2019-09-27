from __future__ import print_function  # In python 2.7
from flask import request, jsonify, Blueprint, abort
import sys
import json
from project.api.models import UserModel
from database import db, bcrypt

users_blueprint = Blueprint('user', __name__)

# User Registration Route
@users_blueprint.route('/auth/registration', methods=['POST'])
def user_registration():
    post_data = request.json
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.\n'
    }

    if(not request.is_json or not post_data):
        return jsonify(response_object), 400

    if UserModel.find_by_email(post_data['email']):
        response_object['message'] = '{} already exists'. format(
            post_data['email'])
        return jsonify(response_object), 400

    name = post_data["name"]
    email = post_data["email"]
    cpf = post_data["cpf"]
    password = post_data["password"]
    url_avatar = post_data["url_avatar"]
    user = UserModel(name, email, cpf, password, url_avatar)

    try:
        user.save_to_db()
        response_object["status"] = 'success'
        response_object["message"] = 'User {} was created'.format(
            post_data["name"])
        return jsonify(response_object), 200
    except:
        response_object["status"] = 'fail'
        response_object["message"] = 'Erro conectando ao db'
        return jsonify(response_object), 400
        # User Login Route


@users_blueprint.route('/auth/login', methods=['POST'])
def user_login():
    post_data = request.json

    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.\n'
    }

    if(not request.is_json or not post_data):
        return jsonify(response_object), 400

    current_user = UserModel.find_by_email(post_data['email'])
    if not current_user:
        response_object['message'] = 'User {} doesn\'t exist'.format(
            post_data['email'])
        return jsonify(response_object), 400

    if current_user and bcrypt.check_password_hash(current_user.password, post_data['password']):
        return {'message': 'Logged in as {}'.format(current_user.username)}
    else:
        return {'message': 'Wrong credentials'}

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
