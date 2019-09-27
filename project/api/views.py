from flask import request, jsonify, Blueprint
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument(
    'username', help='This field cannot be blank', required=True)
parser.add_argument(
    'password', help='This field cannot be blank', required=True)

users_blueprint = Blueprint('user', __name__)

# User Registration Route
@users_blueprint.route('/users/registration', methods=['POST'])
def user_registration():
    data = parser.parse_args()
    return jsonify({
        data
    })

# User Login Route
@users_blueprint.route('/users/login', methods=['POST'])
def user_login():
    data = parser.parse_args()
    return jsonify({
        data
    })

# Logout for access
@users_blueprint.route('/users/logout/access', methods=['POST'])
def user_logout_access():
    return jsonify({
        'message': 'logoutAccess'
    })

# Logout for Refresh Token
@users_blueprint.route('/users/logout/refresh', methods=['POST'])
def user_logout_refresh():
    return jsonify({
        'message': 'logoutRefresh'
    })

# Token Refresh
@users_blueprint.route('/users/token/refresh', methods=['POST'])
def user_token_refresh():
    return jsonify({
        'message': 'tokenRefresh'
    })

# Test Propourses (will be removed)
@users_blueprint.route('/users/all', methods=['GET', 'DELETE'])
def all_users():
    if request.method == 'GET':
        return jsonify({
            'message': 'allUsersGet'
        })
    else:
        return jsonify({
            'message': 'allUsersDelete'
        })

# secret endpoint (to test access with tokens)
@users_blueprint.route('/secret-resource', methods=['GET'])
def all_users():
    return jsonify({
        'answer': 42
    })
