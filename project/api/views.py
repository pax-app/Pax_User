from flask import request, jsonify, Blueprint


users_blueprint = Blueprint('user', __name__)

# User Registration Route
@users_blueprint.route('/auth/registration', methods=['POST'])
def user_registration():
    return jsonify({
        'message': 'registration'
    })

# User Login Route
@users_blueprint.route('/auth/login', methods=['POST'])
def user_login():
    return jsonify({
        'message': 'login'
    })

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

# Test Propourses (will be removed)
@users_blueprint.route('/auth/all', methods=['GET', 'DELETE'])
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
def secret_resource():
    return jsonify({
        'answer': 42
    })
