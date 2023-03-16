from flask_login import current_user
from flask_restx import Resource, Namespace
from flask import request

from application.errors import BadRequestErrors, AuthenticationErrors
from application.service import AuthService
from application.service.main.location import LocationService
from application.setup.api.parsers import locations_parser
from application.setup.db import db
from application.setup.api.models import error
from application.utils.security import check_user, compare_passwords
from application.utils.useful_features import check_id, check_on_space

locations_ns = Namespace('locations')


@locations_ns.route('/')
@locations_ns.response(code=401, description='Invalid credentails', model=error)
class LocationView(Resource):

    @locations_ns.expect(locations_parser)
    @locations_ns.response(code=400, description='Bad request', model=error)
    def post(self):
        """
        - request
        Body {
        "latitude": "double", 	// Географическая широта в градусах
                "longitude": "double" 	// Географическая долгота в градусах
            }

        - response
        Body {
            "id": "long",		// Идентификатор точки локации
            "latitude": "double", 	// Географическая широта в градусах
                "longitude": "double" 	// Географическая долгота в градусах
            }
        :return: json WITH LOCATION
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        location = LocationService(db.session).add_new_location(**locations_parser.parse_args())

        return location, 201


@locations_ns.route('/<string:point_id>')
class LocationView(Resource):
    @locations_ns.response(code=200, description='Success')
    @locations_ns.response(code=400, description='Bad reqeust', model=error)
    @locations_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @locations_ns.response(code=404, description='This accounts not found', model=error)
    def get(self, point_id: str):
        """
        Get accounts by ID if you have rights
        :return: JSON
                - request
        Body {
            empty
        }

                - response
        Body {
            "id": "long",		// Идентификатор точки локации
            "latitude": "double", 	// Географическая широта в градусах
            "longitude": "double" 	// Географическая долгота в градусах
            }
        """
        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        point_id = check_id(point_id)

        location = LocationService(db.session).get_item(point_id)
        return location, 200

    @locations_ns.expect(locations_parser)
    @locations_ns.response(code=200, description='Success', )
    @locations_ns.response(code=400, description='Bad reqeust', model=error)
    @locations_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @locations_ns.response(code=403, description='This accounts not found or you haven"t rights', model=error)
    @locations_ns.response(code=409, description='This email not found', model=error)
    def put(self, point_id: str):
        """
        Update data user if you have rights
        :return: status_code
                - request
        Body {
            "latitude": "double", 	// Новая географическая широта в градусах
            "longitude": "double" 	// Новая географическая долгота в градусах
            }

                - response
        Body {
            "id": "long",		// Идентификатор точки локации
            "latitude": "double", 	// Новая географическая широта в градусах
            "longitude": "double" 	// Новая географическая долгота в градусах
            }

        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        point_id = check_id(point_id)

        location = LocationService(db.session).update_location(point_id=point_id, **locations_parser.parse_args())
        return location, 200

    @locations_ns.response(code=200, description='Success')
    @locations_ns.response(code=400, description='Bad reqeust', model=error)
    @locations_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @locations_ns.response(code=403, description='This accounts not found or you haven"t rights', model=error)
    def delete(self, point_id):

        """
            - request
        Body {
            empty
        }


            - response
        Body {
            empty
        }
        :param point_id:
        :return: none
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        point_id = check_id(point_id)

        LocationService(db.session).delete_location(point_id=point_id)
        return None, 200


