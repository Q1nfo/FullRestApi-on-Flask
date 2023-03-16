from contextlib import suppress
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError

from marshmallow import Schema, fields

from application.dao.base import BaseDAO
from application.errors import ConflictError, BadRequestErrors
from application.models import User


class UserDAO(BaseDAO[User]):
    __model__ = User

    @staticmethod
    def serialize_user(user_obj: User):
        """FUNC TO CREATE JSON FILE"""
        return {
            'id': user_obj.id,
            'firstName': user_obj.firstName,
            'lastName': user_obj.lastName,
            'email': user_obj.email
        }

    def create(self, email: str, password: str, first_name: str, last_name: str) -> dict[str, Any]:
        """CREATE USER IN DB """
        obj = User(email=email, password=password, firstName=first_name, lastName=last_name)
        try:
            self.db_session.add(obj)
            self.db_session.commit()
        except IntegrityError:
            raise ConflictError('User with this email already exists. Choose the different email address.')
        return self.serialize_user(obj)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db_session.query(User).filter(User.email == email).first()

    def update(self, user_id: int, **kwargs) -> User:

        self.db_session.query(User).filter(User.id == user_id).update(kwargs)
        self.db_session.commit()

        return self.get_by_id(user_id)

    def update_password(self, user_id: str, password: str) -> None:
        """UPDATE PASSWORD FROM DB INTO USER"""
        self.db_session.query(User).filter(User.id == user_id).update({
            'password': password
        })
        self.db_session.commit()

    def __get_limit_and_offset(self, page: int,) -> Tuple[int, int]:
        """PANGINATE FUNCTION"""
        limit = self._items_per_page
        offset = 0 if page < 1 else limit * (page - 1)
        return limit, offset

    # .