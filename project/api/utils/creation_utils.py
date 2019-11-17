import requests
from database_singleton import Singleton
from project.api.models import ProviderModel, UserModel, WorksModel
from flask import request, jsonify

db = Singleton().database_connection()


class DatabaseQueries:

    def get_works_relationships(self, provider_id, provider_category_id):
        works = WorksModel.query.filter_by(
            provider_category_id=int(provider_category_id), provider_id=int(provider_id)).first()

    def get_providers_by_category(self, provider_category_id):
        providers = [PROVIDERS.to_json() for PROVIDERS in WorksModel.query.filter_by(
            provider_category_id=(provider_category_id))]

        return providers

    def get_providers_infos_from_dict(self, providers):
        providers_info = [PROVIDERS_INFO.to_json() for PROVIDERS_INFO in ProviderModel.query.filter(
            ProviderModel.provider_id.in_([provider['provider_id'] for provider in providers]))]

        return providers_info

    def get_providers_names(self, providers_info):
        provider_names = [PROVIDER_NAMES.to_json() for PROVIDER_NAMES in UserModel.query.filter(
            UserModel.user_id.in_([provider_info['user_id'] for provider_info in providers_info]))]

        return provider_names


class Utils:
    def append_username_to_provider(self, provider_category_id):
        database_queries = DatabaseQueries()
        providers_category = database_queries.get_providers_by_category(
            provider_category_id)
        providers_info = database_queries.get_providers_infos_from_dict(
            providers_category)
        provider_names = database_queries.get_providers_names(providers_info)

        count = 0
        while(count < len(providers_info)):
            providers_info[count]['name'] = provider_names[count]['name']
            count += 1

        return providers_info

    def consult_provider_review(self, provider_id):
        try:
            response = requests.get(
                'https://pax-gateway.herokuapp.com/api/v1/review/service_reviews/average/{}'.format(provider_id))
            response_json = response.json()
            if response.status_code != 200:
                provider_review = 0
            else:
                provider_review = response_json['provider_service_review_average']
        except ConnectionError:
            provider_review = 0
        return provider_review

    def append_review_to_provider(self, providers_info):
        for provider in providers_info:
            provider_id = int(provider['provider_id'])
            provider_review = self.consult_provider_review(provider_id)
            provider['reviews_average'] = provider_review
        return providers_info

    def createFailMessage(self, message):
        response_object = {
            'status': 'fail',
            'message': '{}'.format(message)
        }
        return response_object

    def createSuccessMessage(self, message):
        response_object = {
            'status': 'success',
            'message': '{}'.format(message)
        }
        return response_object
