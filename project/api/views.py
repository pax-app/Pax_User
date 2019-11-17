from project.api.models import UserModel, WorksModel, ProviderModel, AddressModel, LivesModel
from project.api.utils.display_strategy import Context, ReviewStrategy, PriceStrategy
from project.api.utils.creation_utils import DatabaseQueries, Utils
from project.api.utils.auth_utils import authenticate
from flask import request, jsonify, Blueprint
from database_singleton import Singleton
from project.api import bcrypt
from sqlalchemy import and_
import json
import requests

users_blueprint = Blueprint('user', __name__)
providers_categories_blueprint = Blueprint('provider_category', __name__)
db = Singleton().database_connection()

# User Registration Route
@users_blueprint.route('/auth/registration', methods=['POST'])
def user_registration():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(Utils().createFailMessage("Invalid Payload")), 400

    db.session.rollback()
    name = post_data["name"]
    email = post_data["email"]
    cpf = post_data["cpf"]
    password = post_data["password"]
    url_avatar = post_data["url_avatar"]
    user = UserModel(name, email, cpf, password, url_avatar)

    if UserModel.find_by_email(email):
        return jsonify(Utils().createFailMessage('{} already exists'.format(email))), 400

    try:
        user.save_to_db()
        auth_token = user.encode_auth_token(user.user_id)
        response_object = Utils().createSuccessMessage('User was created')
        user = UserModel.find_by_email(email)
        provider = ProviderModel.find_provider(user.user_id)
        response_object["auth_token"] = auth_token.decode()
        response_object["name"] = name
        response_object["email"] = email
        response_object["id"] = user.user_id
        response_object["is_provider"] = provider is not None
        return jsonify(response_object), 201
    except:
        db.session.rollback()
        return jsonify(Utils().createFailMessage('Try again later')), 503
        # User Login Route


@users_blueprint.route('/auth/login', methods=['POST'])
def user_login():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(Utils().createFailMessage("Invalid Payload")), 400

    email = post_data["email"]
    password = post_data["password"]

    try:
        current_user = UserModel.find_by_email(email)

        if not current_user:
            return jsonify(Utils().createFailMessage('User {} doesn\'t exist'.format(email))), 404

        if current_user and bcrypt.check_password_hash(current_user.password, password):
            provider = ProviderModel.find_provider(current_user.user_id)
            auth_token = current_user.encode_auth_token(current_user.user_id)
            response_object = Utils().createSuccessMessage('Successfully logged in.')
            response_object["auth_token"] = auth_token.decode()
            response_object["name"] = current_user.name
            response_object["email"] = current_user.email
            response_object["id"] = current_user.user_id
            response_object["is_provider"] = provider is not None

            return jsonify(response_object), 200
        else:
            return jsonify(Utils().createFailMessage('Wrong Credentials')), 401
    except Exception as ex:
        db.session.rollback()
        return jsonify(Utils().createFailMessage(ex)), 500

# Logout for access
@users_blueprint.route('/auth/logout', methods=['GET'])
def user_logout(resp):
    response_object = {
        'status': 'success',
        'message': 'Successfully logged out.'
    }
    return jsonify(response_object), 200


@users_blueprint.route('/auth/status', methods=['GET'])
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
def provider_registration(resp):
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(Utils().createFailMessage("Invalid Payload")), 400
    db.session.rollback()
    minimum_price = post_data["minimum_price"]
    maximum_price = post_data["maximum_price"]
    bio = post_data["bio"]
    url_rg_photo = post_data["url_rg_photo"]
    url_avatar = post_data["url_avatar"]
    number = post_data["number"]
    user_id = post_data["user_id"]
    provider_categories = post_data["categories"]
    categories = json.loads(provider_categories)

    user = UserModel.find(user_id)
    try:
        user.url_avatar = url_avatar
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(Utils().createFailMessage('Error saving picture')), 500

    provider = ProviderModel(minimum_price, maximum_price,
                             bio, url_rg_photo, number, user_id)

    try:
        provider.save_to_db()
        response_object = Utils().createSuccessMessage('Provider was created')
        provider = ProviderModel.find_provider(user_id)
        for category in categories:
            work = WorksModel(category["id"], provider.provider_id)
            work.save_to_db()

        return jsonify(response_object), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(Utils().createFailMessage('Try again later')), 503


@users_blueprint.route('/add_address', methods=['POST'])
def add_address():
    post_data = request.json

    if(not request.is_json or not post_data):
        return jsonify(Utils().createFailMessage("Invalid Payload")), 400

    user_id = post_data["user_id"]
    street = post_data["street"]
    neighborhood = post_data["neighborhood"]
    number = post_data["number"]
    city = post_data["city"]
    cep = post_data["cep"]
    state = post_data["state"]

    try:
        complement = post_data["complement"]
    except:
        complement = None

    try:
        reference_point = post_data["reference_point"]
    except:
        reference_point = None

    address = AddressModel(street, neighborhood, number,
                           complement, city, cep, state, reference_point)

    try:
        address.save_to_db()
    except:
        db.session.rollback()
        return jsonify(Utils().createFailMessage('Try again later')), 503

    lives = LivesModel(user_id, address.address_id)

    try:
        lives.save_to_db()
        response_object = Utils().createSuccessMessage('Address registered')
        return jsonify(response_object), 201
    except:
        db.session.rollback()
        return jsonify(Utils().createFailMessage('Try again later')), 503


@users_blueprint.route('/get_user_info/<user_type>/<id>', methods=['GET'])
def get_user_info(user_type, id):
    user_id = id

    if(user_type == 'provider'):
        user_id = ProviderModel.query.filter_by(provider_id=id).first().user_id

    row = UserModel.query.filter_by(user_id=user_id).first()

    response = {
        "username": row.name,
        "url_avatar": row.url_avatar
    }

    return jsonify(response)


@users_blueprint.route('/get_address/<address_id>', methods=['GET'])
def get_address(address_id):
    row = AddressModel.query.filter_by(address_id=address_id).all()

    return jsonify([address.to_json() for address in row][0]), 200


@users_blueprint.route('/get_addresses/<user_id>', methods=['GET'])
def get_addresses(user_id):
    addresses = AddressModel.query.join(
        LivesModel, and_(LivesModel.user_id == user_id, LivesModel.address_id == AddressModel.address_id))

    return jsonify([row.to_json() for row in addresses]), 200

# User id validation needed at Gateway API
@providers_categories_blueprint.route('/<provider_id>/category_provider/<provider_category_id>', methods=['DELETE'])
def remove_category_provider_relationship(provider_id, provider_category_id):
    works = WorksModel.query.filter_by(
        provider_category_id=int(provider_category_id), provider_id=int(provider_id)).first()

    if not works:
        return jsonify(Utils().createFailMessage('Relationship Not Found')), 404

    db.session.delete(works)
    db.session.commit()

    return jsonify(Utils().createSuccessMessage('Relationship deleted!')), 200


@providers_categories_blueprint.route('/provider_by_category/min_price/<provider_category_id>', methods=['GET'])
def get_providers_by_category_min_price(provider_category_id):
    utils = Utils()
    # Adding the provider's name field to provider's info returned
    providers_info = utils.append_username_to_provider(provider_category_id)

    if not providers_info:
        response = {
            'status': 'failed',
            'error': "ID Not Found"
        }
        return jsonify(response), 404

    context = Context(PriceStrategy())
    providers_info = context.execute_sorting(provider_category_id)
    return jsonify(providers_info), 200


@providers_categories_blueprint.route('/provider_by_category/review/<provider_category_id>', methods=['GET'])
def order_providers_by_review(provider_category_id):
    utils = Utils()
    # Adding the provider's name field to provider's info returned
    providers_info = utils.append_username_to_provider(provider_category_id)
    providers_info = utils.append_review_to_provider(providers_info)
    context = Context(ReviewStrategy())
    providers_info = context.execute_sorting(provider_category_id)

    return jsonify(providers_info), 200
