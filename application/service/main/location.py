from typing import List, Optional, Dict, Any

from application.dao.main.location import LocationDAO
from application.models import Location
from application.service.base import BaseService
from application.errors import BadRequestErrors


# =====================LOCATIONS SERVICE WHERE DO BUSINESS LOGIC =============================================
# .
class LocationService(BaseService):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
        self._accounts_dao = LocationDAO(db_session)

    @staticmethod
    def serialize_location(location: Location):
        return {
            'id': location.id,
            'latitude': location.latitude,
            'longitude': location.longitude
        }

    def get_item(self, location_id: int) -> dict[str, Any]:
        return self.serialize_location(self._accounts_dao.get_by_id(location_id))

    @staticmethod
    def _check_location_data(latitude: int, longitude: int):

        if '' or None in [latitude, longitude]:
            raise BadRequestErrors

        if int(latitude) < (-90) or int(latitude) > 90:
            raise BadRequestErrors
        if int(longitude) < (-180) or int(longitude) > 180:
            raise BadRequestErrors

    def add_new_location(self, **kwargs):
        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')

        self._check_location_data(latitude=latitude, longitude=longitude)

        return self.serialize_location(self._accounts_dao.add_new_location(longitude=longitude, latitude=latitude))

    def update_location(self, point_id: int, **kwargs):
        latitude = kwargs.get('latitude')
        longitude = kwargs.get('longitude')

        self._check_location_data(latitude=latitude, longitude=longitude)

        return self.serialize_location(
            self._accounts_dao.update_location(point_id, longitude=longitude, latitude=latitude))

    def delete_location(self, point_id: int) -> None:
        self._accounts_dao.remove_location(point_id)
