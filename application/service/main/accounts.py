from typing import List, Optional

from flask import request, abort

from application.dao import UserDAO, AccountsDAO
from application.errors import BadRequestErrors, ConflictError, AuthenticationErrors, RequestFromAuthorizedAccountErrors
from application.models import User
from application.service.base import BaseService
from application.utils.security import generate_password_hash
from application.utils.useful_features import check_on_null
# .

# =====================MAIN FUNCTION FROM ACCOUNTS SERVICE WHERE DO BUSINESS LOGIC ====================================

class AccountsService(BaseService):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
        self._accounts_dao = AccountsDAO(db_session)
        self._user_dao = UserDAO(db_session)

    def get_item(self, account_id: int) -> User:
        return self._accounts_dao.get_by_id(account_id)

    def get_by_param(self):
        """SEARCHING SYSTEM"""

        name = request.args.get('firstName')
        surname = request.args.get('lastName')
        email = request.args.get('email')
        from_ = request.args.get('from')
        size = request.args.get('size')

        if from_:
            if int(from_) < 0:
                raise BadRequestErrors
        if size:
            if int(size) <= 0:
                raise BadRequestErrors

        return self._accounts_dao.get_by_param(name=name, surname=surname, email=email, from_=from_,
                                               size=size)

    def update_user_profile(self, user_id: int, **kwargs):

        if check_on_null(**kwargs):
            raise BadRequestErrors

        data = {
                'firstName': kwargs.get('firstName'),
                'lastName': kwargs.get('lastName'),
                'email': kwargs.get('email'),
                'password': generate_password_hash(kwargs.get('password'))
            }

        return self._accounts_dao.update_user_profile(user_id=user_id, **data)

    def delete_user(self, user_id: int) -> None:
        self._accounts_dao.remove_user(user_id)

