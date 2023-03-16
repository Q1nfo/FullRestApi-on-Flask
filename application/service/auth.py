from typing import Dict, Any

from marshmallow.fields import Email, Integer
from marshmallow.schema import BaseSchema

from application.dao.auth import UserDAO
from application.errors import AuthenticationErrors, BadRequestErrors
from application.models import User
from application.service.base import BaseService
from application.utils.jwt_token import JwtToken
from application.utils.security import compare_passwords, generate_password_hash


class UserSchema(BaseSchema):
    """CLASS TO SERIALIZE MANY SET OF USER DATA"""
    id = Integer(required=True)
    email = Email(required=True)


# =====================AUTH SERVICE WHERE DO BUSINESS LOGIC =============================================
class AuthService(BaseService):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
        self.dao = UserDAO(db_session)
        self.schema = UserSchema()

    @staticmethod
    def serialize_user(user_obj: User):
        return {
            'id': user_obj.id,
            'firstName': user_obj.firstName,
            'lastName': user_obj.lastName,
            'email': user_obj.email
        }

    # .
    def register_user(self, **kwargs) -> dict[str, Any]:
        first_name = kwargs.get('firstName').lower()
        last_name = kwargs.get('lastName').lower()
        password = kwargs.get('password')
        email = kwargs.get('email').lower()

        if '' or None in [first_name, last_name, password, email]:
            raise BadRequestErrors

        new_user = self.dao.create(email=email, password=generate_password_hash(password), first_name=first_name,
                                   last_name=last_name)

        return new_user

    def get_user_by_email(self, **kwargs):
        user = self.dao.get_user_by_email(email=kwargs.get('login'))
        return user

    def check_user_credentials(self, email: str, password: str) -> Dict[str, str]:
        """COMPARE USER DATA WITH DATA IN DB ABOUT USER"""
        if not (user := self.dao.get_user_by_email(email)):
            raise AuthenticationErrors

        if not compare_passwords(user.password, password):
            raise AuthenticationErrors

        return JwtToken(self.schema.dump(user)).get_tokens()

    def get_user_profile(self, user_id: int) -> dict[str, Any]:
        return self.serialize_user(self.dao.get_by_id(pk=user_id))

    def update_user_password(self, user_id: int, old_password: str, new_password: str) -> None:
        if user := self.dao.get_by_id(pk=user_id):
            if compare_passwords(user.password, old_password):
                self.dao.update_password(
                    user_id=user_id,
                    password=generate_password_hash(new_password)
                )
                return None

        raise BadRequestErrors('Fail to change user password')

    def get_user(self, email: str):
        return self.dao.get_user_by_email(email=email)
