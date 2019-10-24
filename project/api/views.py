import requests
from flask import request, jsonify, Blueprint
from project.api.models import UserModel, WorksModel, ProviderModel
from database_singleton import Singleton
from project.api import bcrypt
from project.api.auth_utils import authenticate

users_blueprint = Blueprint('user', __name__)
providers_categories_blueprint = Blueprint('provider_category', __name__)
db = Singleton().database_connection()


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
        response_object["name"] = name
        response_object["email"] = email
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
            response_object["name"] = current_user.name
            response_object["email"] = current_user.email
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

# Provider Registration Route
@users_blueprint.route('/provider_registration', methods=['POST'])
def provider_registration():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(createFailMessage("Invalid Payload")), 400

    minimum_price = post_data["minimum_price"]
    maximum_price = post_data["maximum_price"]
    bio = post_data["bio"]
    url_rg_photo = post_data["url_rg_photo"]
    number = post_data["number"]
    user_id = post_data["user_id"]
    # TODO: Use the received categories to reg. provider categories at the categories service
    provider_categories = post_data["categories"]

    provider = ProviderModel(minimum_price, maximum_price,
                             bio, url_rg_photo, number, user_id)

    try:
        provider.save_to_db()
        response_object = createSuccessMessage('Provider was created')
        return jsonify(response_object), 201
    except:
        db.session.rollback()
        return jsonify(createFailMessage('Try again later')), 503

# User id validation needed at Gateway API
@providers_categories_blueprint.route('/<provider_id>/category_provider/<provider_category_id>', methods=['DELETE'])
def remove_category_provider_relationship(provider_id, provider_category_id):
    works = WorksModel.query.filter_by(
        provider_category_id=int(provider_category_id), provider_id=int(provider_id)).first()

    if not works:
        return jsonify(createFailMessage('Relationship Not Found')), 404

    db.session.delete(works)
    db.session.commit()

    return jsonify(createSuccessMessage('Relationship deleted!')), 200


@providers_categories_blueprint.route('/provider_by_category/<provider_category_id>', methods=['GET'])
def get_providers_by_category(provider_category_id):

    # Getting providers in the specific category
    providers = [PROVIDERS.to_json() for PROVIDERS in WorksModel.query.filter_by(
        provider_category_id=(provider_category_id))]

    # Getting info of the selected providers
    providers_info = [PROVIDERS_INFO.to_json() for PROVIDERS_INFO in ProviderModel.query.filter(
        ProviderModel.provider_id.in_([provider['provider_id'] for provider in providers]))]

    # Getting the name of selected providers
    provider_names = [PROVIDER_NAMES.to_json() for PROVIDER_NAMES in UserModel.query.filter(
        UserModel.user_id.in_([provider_info['user_id'] for provider_info in providers_info]))]
    # TODO:Convert this two queries to a join on the foreign key user_id, so that the while loop is no longer necessary

    # Adding the provider's name field to provider's info returned

    count = 0
    while(count < len(providers_info)):

        providers_info[count]['name'] = provider_names[count]['name']

        count += 1

    if not providers:
        response = {
            'status': 'failed',
            'error': "ID Not Found"
        }
        return jsonify(response), 404

    return jsonify(providers_info), 200


@providers_categories_blueprint.route('/provider_by_category/min_price/<provider_category_id>', methods=['GET'])
def get_providers_by_category_min_price(provider_category_id):

    # Getting providers in the specific category
    providers = [PROVIDERS.to_json() for PROVIDERS in WorksModel.query.filter_by(
        provider_category_id=(provider_category_id))]

    # Getting info of the selected providers
    providers_info = [PROVIDERS_INFO.to_json() for PROVIDERS_INFO in ProviderModel.query.filter(
        ProviderModel.provider_id.in_([provider['provider_id'] for provider in providers]))]

    # Getting the name of selected providers
    provider_names = [PROVIDER_NAMES.to_json() for PROVIDER_NAMES in UserModel.query.filter(
        UserModel.user_id.in_([provider_info['user_id'] for provider_info in providers_info]))]
    # TODO:Convert this two queries to a join on the foreign key user_id, so that the while loop is no longer necessary

    # Adding the provider's name field to provider's info returned

    count = 0
    while(count < len(providers_info)):

        providers_info[count]['name'] = provider_names[count]['name']

        count += 1

    providers_info = sorted(
        providers_info, key=lambda element: element['minimum_price'])

    if not providers:
        response = {
            'status': 'failed',
            'error': "ID Not Found"
        }
        return jsonify(response), 404

    return jsonify(providers_info), 200


@providers_categories_blueprint.route('/provider_by_category/review/<provider_category_id>', methods=['GET'])
def order_providers_by_review(provider_category_id):

    providers = [PROVIDERS.to_json() for PROVIDERS in WorksModel.query.filter_by(
        provider_category_id=(provider_category_id))]

    # Getting info of the selected providers
    providers_info = [PROVIDERS_INFO.to_json() for PROVIDERS_INFO in ProviderModel.query.filter(
        ProviderModel.provider_id.in_([provider['provider_id'] for provider in providers]))]

    # Getting the name of selected providers
    provider_names = [PROVIDER_NAMES.to_json() for PROVIDER_NAMES in UserModel.query.filter(
        UserModel.user_id.in_([provider_info['user_id'] for provider_info in providers_info]))]
    # TODO:Convert this two queries to a join on the foreign key user_id, so that the while loop is no longer necessary

    # Adding the provider's name field to provider's info returned

    count = 0
    while(count < len(providers_info)):

        providers_info[count]['name'] = provider_names[count]['name']
        providers_info[count]['reviews_average'] = 0.0
        count += 1

    try:
        for provider in providers_info:
            provider_id = int(provider['provider_id'])
            reviews_response = requests.get(
                'http://172.22.0.1:5004/service_reviews/average/{}'.format(provider_id))
            if not reviews_response:
                return jsonify('Inexistent id in review service'), 404
            reviews_response = reviews_response.json()
            if provider['provider_id'] == provider_id:
                provider['reviews_average'] = reviews_response["provider_service_review_average"]

    except ConnectionError:
        return jsonfiy(createFailMessage('Could not connect to review service')), 400

    providers_info = sorted(
        providers_info, key=lambda element: element['reviews_average'])

    return jsonify(providers_info), 200
