from typing import Optional, Any, Type

from flask_sqlalchemy import BaseQuery
from sqlalchemy import desc, and_

from application.dao.base import BaseDAO
from application.errors import BadRequestErrors, ConflictError
from application.models import Location


# =====================MAIN DAO FROM LOCATION ENDPOINT =============================================
class LocationDAO(BaseDAO[Location]):
    __model__ = Location

    def add_new_location(self, latitude: int, longitude: int) -> Location:

        if self.db_session.query(Location).filter(and_(Location.latitude == latitude,
                                                       Location.longitude == longitude)).all():
            raise ConflictError

        obj = Location(latitude=latitude, longitude=longitude)

        try:
            self.db_session.add(obj)
            self.db_session.commit()
        except Exception():
            raise BadRequestErrors

        return obj

    def get_all(self, page: Optional[int] = None, new: bool = False) -> list[Type[Location]] | Any:
        stmt: BaseQuery = self.db_session.query(Location)
        if new:
            stmt: BaseQuery = stmt.order_by(desc(Location.name))
        if page:
            return stmt.paginate(page=page, per_page=self._items_per_page).items
        return stmt.all()

    def update_location(self, longitude_id: int, latitude: int, longitude: int) -> Location:

        location = self.db_session.query(self.__model__).get_or_404(longitude_id)

        if self.db_session.query(Location).filter(and_(Location.latitude == latitude,
                                                       Location.longitude == longitude)).all():
            raise ConflictError

        location.latitude = latitude
        location.longitude = longitude
        self.db_session.commit()

        return self.get_by_id(longitude_id)

    def remove_location(self, location_id: int) -> None:

        location = self.get_by_id(location_id)

        if location.animals:
            raise BadRequestErrors

        self.db_session.delete(location)
        self.db_session.commit()


# .
