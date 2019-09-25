from flask import request, jsonify, Blueprint

user_blueprint = Blueprint('user', __name__)


@users_blueprint.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
