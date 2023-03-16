from flask import request
from flask_restx import Namespace, Resource

from application.errors import BadRequestErrors, RequestFromAuthorizedAccountErrors
from application.utils.useful_features import check_on_space

from application.service.auth import AuthService
from application.setup.api.models import error
from application.setup.api.parsers import registration_parser
from application.setup.db import db

auth_ns = Namespace('registration')


@auth_ns.route('/')
class RegisterUserView(Resource):

    @auth_ns.expect(registration_parser)
    @auth_ns.response(code=201, description='Created', headers={'Location': 'The URL of a newly created user'})
    @auth_ns.response(code=400, description='Bad reqeust', model=error)
    @auth_ns.response(code=403, description='Request from Authorisation User', model=error)
    @auth_ns.response(code=409, description='This EMAIL not found', model=error)
    def post(self):
        """
        Add new user
        :return: JSON of new user.
        """
        """POST - /registration

        - request
        Body {
        "firstName": "string",	// Имя пользователя
        "lastName": "string",	// Фамилия пользователя
        "email": "string",	// Адрес электронной почты
        "password": "string"	// Пароль от аккаунта пользователя
        }

        - response
        Body {
        “id”: "int",		// Идентификатор аккаунта пользователя
        "firstName": "string",	// Имя пользователя
        "lastName": "string",	// Фамилия пользователя
        "email": "string"	// Адрес электронной почты
        }

        """
        if request.headers.get('Authorization'):
            raise RequestFromAuthorizedAccountErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        user = AuthService(db.session).register_user(**registration_parser.parse_args())

        return user, 201
