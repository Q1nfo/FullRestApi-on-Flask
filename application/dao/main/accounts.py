import json
from typing import List, Optional, Any, Type

from flask_sqlalchemy import BaseQuery
from sqlalchemy import desc, asc, and_

from application.dao.base import BaseDAO
from application.errors import BadRequestErrors, RequestFromAuthorizedAccountErrors, ConflictError
from application.models import User, Animal


class AccountsDAO(BaseDAO[User]):
    __model__ = User

    @staticmethod
    def serialize_user(user_obj: User):
        return {
            'id': user_obj.id,
            'firstName': user_obj.firstName,
            'lastName': user_obj.lastName,
            'email': user_obj.email
        }

    def get_all(self, page: Optional[int] = None, new: bool = False) -> list[Type[User]] | Any:
        """RETURN ALL OBJECT IN DB """
        stmt: BaseQuery = self.db_session.query(User)
        if new:
            stmt: BaseQuery = stmt.order_by(desc(User.name))
        if page:
            return stmt.paginate(page=page, per_page=self._items_per_page).items
        return stmt.all()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """RETURN USER WITH NEEDED EMAIL"""
        return self.db_session.query(User).filter(User.email == email).one_or_none()

    def get_by_param(self, name: str = '', surname: Optional[str] = None, email: Optional[str] = None, from_=0,
                     size=10) -> json:

        """SYSTEM SEARCHING IN ENDPOINT ANIMAL"""

        if from_ is None:
            from_ = 0

        if size is None:
            size = 10

        stmt: BaseQuery = self.db_session.query(User)
        if name:
            if surname:
                if email:
                    stmt = stmt.filter(and_(User.firstName.like(f'%{name}%'),
                                            User.lastName.like(f'%{surname}%'),
                                            User.email.like(f'%{email}%')))
                else:
                    stmt = stmt.filter(and_(User.firstName.like(f'%{name}%'),
                                            User.lastName.like(f'%{surname}%')))
            else:
                if email:
                    stmt = stmt.filter(and_(User.firstName.like(f'%{name}%'),
                                            User.email.like(f'%{email}%')))
                else:
                    stmt = stmt.filter(User.firstName.like(f'%{name}%'))
        else:
            if surname:
                if email:
                    stmt = stmt.filter(and_(User.lastName.like(f'%{surname}%'),
                                            User.email.like(f'%{email}%')))
                else:
                    stmt = stmt.filter(and_(User.lastName.like(f'%{surname}%')))
            else:
                if email:
                    stmt = stmt.filter(User.email.like(f'%{email}%'))

        stmt = stmt.order_by(asc(User.id))

        if from_:
            stmt = stmt.offset(int(from_))
        if size:
            stmt = stmt.limit(int(size))

        return stmt.all()

    def update_user_profile(self, user_id: int, **kwargs) -> dict[str, Any]:

        """UPDATE PROFILES IN PUT METHOD"""

        if (user := self.get_by_id(user_id)) and user.email == kwargs.get('email'):
            if list_user := self.db_session.query(User).filter(User.email == kwargs.get('email')).all():
                if len(list(list_user)) > 1:
                    raise ConflictError
        else:
            if self.db_session.query(User).filter(User.email == kwargs.get('email')).all():
                raise ConflictError

        self.db_session.query(User).filter(User.id == user_id).update(kwargs)
        self.db_session.commit()
        return self.serialize_user(self.get_by_id(user_id))

    def remove_user(self, user_id: int) -> None:

        """DELETE METHOD"""

        if self.db_session.query(Animal).filter(Animal.chipperId == user_id).all():
            raise BadRequestErrors

        if not (user := self.db_session.query(User).filter(User.id == user_id).first()):
            raise RequestFromAuthorizedAccountErrors

        self.db_session.delete(user)
        self.db_session.commit()

# .


