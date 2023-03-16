from flask_restx import Resource, Namespace
from flask import request
from marshmallow import Schema, fields

from application.service import AuthService
from application.service.main import AccountsService
from application.setup.api.parsers import registration_parser
from application.setup.db import db
from application.setup.api.models import error
from application.utils.security import check_user, compare_passwords
from application.utils.useful_features import check_id, serialize_to_task_user, check_on_space
from application.errors import BadRequestErrors, AuthenticationErrors, RequestFromAuthorizedAccountErrors

accounts_ns = Namespace('accounts')


class UserSchema(Schema):
    id = fields.Int()
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()


@accounts_ns.route('/<string:account_id>/')
class AccountsView(Resource):

    @accounts_ns.response(code=200, description='Success',)
    @accounts_ns.response(code=400, description='Bad reqeust', model=error)
    @accounts_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @accounts_ns.response(code=404, description='This accounts not found', model=error)
    def get(self, account_id: str):
        """
        Get accounts by ID if you have rights
        :return: JSON
        """
        """- request
        Body {
            empty
        }					
                
        - response
        Body {
        "id": "int",		// Идентификатор аккаунта пользователя
        "firstName": "string",	// Имя пользователя
        "lastName": "string",	// Фамилия пользователя
        "email": "string"	// Адрес электронной почты
        }
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))
        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        account_id = check_id(account_id)

        user = AuthService(db.session).get_user_profile(account_id)
        return user, 200

    @accounts_ns.expect(registration_parser)
    @accounts_ns.response(code=200, description='Success', )
    @accounts_ns.response(code=400, description='Bad reqeust', model=error)
    @accounts_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @accounts_ns.response(code=403, description='This accounts not found or you haven"t rights', model=error)
    @accounts_ns.response(code=409, description='This email not found', model=error)
    def put(self, account_id: str):
        """
        Update data user if you have rights
        :return: status_code
        - request
        Body {
        "firstName": "string",	// Новое имя пользователя
        "lastName": "string",	// Новая фамилия пользователя
        "email": "string",	// Новый адрес электронной почты
        "password": "string"    // Пароль от аккаунта
        }

        - response
        Body {
        "id": "int",		// Идентификатор аккаунта пользователя
        "firstName": "string",	// Новое имя пользователя
        "lastName": "string",	// Новая фамилия пользователя
        "email": "string"	// Новый адрес электронной почты
        }

        """
        account_id = check_id(account_id)

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if current_user.id != account_id:
            raise RequestFromAuthorizedAccountErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        user = AccountsService(db.session).update_user_profile(user_id=account_id, **registration_parser.parse_args())

        return user, 200

    @accounts_ns.response(code=200, description='Success')
    @accounts_ns.response(code=400, description='Bad reqeust', model=error)
    @accounts_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @accounts_ns.response(code=403, description='This accounts not found or you haven"t rights', model=error)
    def delete(self, account_id):
        """
                - request
        Body {
            empty
        }

        - response
        Body {
                empty
        }
        :param account_id:
        :return: none
        """

        account_id = check_id(account_id)

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if current_user.id != account_id:
            raise RequestFromAuthorizedAccountErrors

        AccountsService(db.session).delete_user(user_id=account_id)
        return None, 200


@accounts_ns.route('/search')
class AccountsView(Resource):

    @accounts_ns.response(code=200, description='Success', )
    @accounts_ns.response(code=400, description='Bad reqeust', model=error)
    @accounts_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    def get(self):
        """
        Get Users by parametrs
        :return: List[User]
        GET - /accounts/search
        ?firstName={firstName}
        &lastName={lastName}
        &email={email}
        &from={from}
        &size={size}
        {firstName}: "string",
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        user = AccountsService(db.session).get_by_param()

        return list(map(serialize_to_task_user, UserSchema(many=True).dump(user))), 200
