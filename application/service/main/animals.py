from datetime import datetime
from typing import Any

from flask import request

from application.dao import AnimalsTypesDAO
from application.dao.main.animals import AnimalsDAO
from application.errors import BadRequestErrors
from application.models import TypeAnimals, Animal
from application.service.base import BaseService


# =====================MAIN ANIMALS SERVICE WHERE DO BUSINEES LOGIC ON PROJECT ========================================

class AnimalsService(BaseService):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
        self._animals_dao = AnimalsDAO(db_session)

    def update_time_location_on_animal(self, animal_id):
        self._animals_dao.update_time_location_on_animal(animal_id)

    @staticmethod
    def _check_request(**kwargs):

        """FUNC TO CHECKING DATA WITCH USER GIVE US"""

        if len(kwargs.get('animalTypes')) <= 0 or None in kwargs.get('animalTypes'):
            raise BadRequestErrors

        if type(kwargs.get('animalTypes')) != list:
            raise BadRequestErrors

        for types in (animalTypes := kwargs.get('animalTypes')):

            if type(types) != int:
                raise BadRequestErrors

            if types == '' or types <= 0 or types is None:
                raise BadRequestErrors

        if '' or None in (data_ := [(weight := kwargs.get('weight')),
                                    (length := kwargs.get('length')),
                                    (height := kwargs.get('height')),
                                    (gender := kwargs.get('gender')),
                                    (chipperId := kwargs.get('chipperId')),
                                    (chippingLocationId := kwargs.get('chippingLocationId'))]):
            raise BadRequestErrors

        for element in data_:

            if type(element) != int:
                continue
            else:

                if element <= 0:
                    raise BadRequestErrors

        if gender not in ['MALE', 'FEMALE', 'OTHER']:
            raise BadRequestErrors

        data = {
            'animalTypes': animalTypes,
            'weight': weight,
            'length': length,
            'height': height,
            'gender': gender,
            'chipperId': chipperId,
            'chippingLocationId': chippingLocationId
        }

        return data

    def get_item(self, animals_id: int) -> Animal:
        return self._animals_dao.get_by_id_new(animals_id)

    def add_new_animals(self, **kwargs):

        data = self._check_request(**kwargs)

        return self._animals_dao.add_new_animals(**data)

    def update_animals(self, animals_id: int, **kwargs):

        if '' or None in (data_ := [(weight := kwargs.get('weight')),
                                    (length := kwargs.get('length')),
                                    (height := kwargs.get('height')),
                                    (gender := kwargs.get('gender')),
                                    (life_status := kwargs.get('lifeStatus')),
                                    (chipperId := kwargs.get('chipperId')),
                                    (chippingLocationId := kwargs.get('chippingLocationId'))]):
            raise BadRequestErrors

        for element in data_:

            if type(element) != int:
                continue
            else:
                if element <= 0:
                    raise BadRequestErrors

        if gender not in ['MALE', 'FEMALE', 'OTHER']:
            raise BadRequestErrors

        if life_status not in ['ALIVE', 'DEAD']:
            raise BadRequestErrors

        data = {
            'weight': weight,
            'length': length,
            'height': height,
            'gender': gender,
            'lifeStatus': life_status,
            'chipperId': chipperId,
            'chippingLocationId': chippingLocationId
        }

        return self._animals_dao.update_animals(animals_id, **data)

    # =====================PRIVATE FUNCTIONS INTO THIS SERVICE =============================================

    def add_new_locations(self, animal_id, location_id):
        return self._animals_dao.add_new_locations(animal_id=animal_id, location_id=location_id)

    def delete_animals(self, animals_id: int) -> None:
        self._animals_dao.remove_animals(animals_id)

    def update_type_on_animals(self, animals_id: int, type_id: int):
        return self._animals_dao.update_type_on_animals(animals_id, type_id)

    def delete_type_on_animals(self, animal_id: int, type_id: int):
        return self._animals_dao.delete_type_on_animals(animal_id, type_id)

    def update_location_on_animals(self, animal_id: int, point_id: int):
        return self._animals_dao.update_location_on_animals(animal_id, point_id)

    def delete_location_on_animals(self, animal_id: int, point_id: int):
        self._animals_dao.delete_location_on_animals(animal_id, point_id)

    # =====================SEARCHING SYSTEM SERVICE =============================================

    def search_animals(self):

        from_ = request.args.get('from')
        size = request.args.get('size')

        if 0 in [from_, size]:
            raise BadRequestErrors

        if size and int(size) <= 0:
            raise BadRequestErrors

        start_date_time = request.args.get('startDateTime')
        end_date_time = request.args.get('endDateTime')

        if start_date_time:
            try:
                start_date = datetime.fromisoformat(start_date_time)
            except ValueError:
                raise BadRequestErrors

        if end_date_time:
            try:
                end_date = datetime.fromisoformat(end_date_time)
            except ValueError:
                raise BadRequestErrors

        if not start_date_time:
            start_date = None

        if not end_date_time:
            end_date = None

        chipper_id = request.args.get('chipperId')
        chipping_location_id = request.args.get('chippingLocationId')

        for kwarg in [chipper_id, chipping_location_id]:
            if type(kwarg) == int:
                if int(kwarg) <= 0:
                    raise BadRequestErrors

        life_status = request.args.get('lifeStatus')

        if life_status and life_status not in ['ALIVE', 'DEAD']:
            raise BadRequestErrors

        gender = request.args.get('gender')

        if gender and gender not in ['MALE', 'FEMALE', 'OTHER']:
            raise BadRequestErrors

        return self._animals_dao.search_animals(start_date=start_date, end_date=end_date)

    def replace_type_on_animals(self, animal_id: int, **kwargs):
        old_type_id = kwargs.get('oldTypeId')
        new_type_id = kwargs.get('newTypeId')

        for id in [old_type_id, new_type_id]:
            if id <= 0 or id == '' or id is None:
                raise BadRequestErrors

        return self._animals_dao.replace_type_on_animals(animal_id, oid=old_type_id, nid=new_type_id)

    def search_locations_on_animals(self, animal_id: int, **kwargs):

        start_date_time = request.args.get('startDateTime')
        end_date_time = request.args.get('endDateTime')

        if start_date_time:
            try:
                start_date = datetime.fromisoformat(start_date_time)
            except ValueError:
                raise BadRequestErrors

        if end_date_time:
            try:
                end_date = datetime.fromisoformat(end_date_time)
            except ValueError:
                raise BadRequestErrors

        if not start_date_time:
            start_date = None

        if not end_date_time:
            end_date = None

        from_ = request.args.get('from')
        size = request.args.get('size')

        if 0 in [from_, size]:
            raise BadRequestErrors

        if size:
            if int(size) <= 0:
                raise BadRequestErrors

        return self._animals_dao.search_locations_on_animals(animal_id=animal_id,
                                                             start_date=start_date,
                                                             end_date=end_date,
                                                             **kwargs)

    def replace_location_on_animal(self, animal_id: int, **kwargs):

        visited_location_id = kwargs.get('visitedLocationPointId')
        location_id = kwargs.get('locationPointId')

        if None in [visited_location_id, location_id]:
            raise BadRequestErrors

        for id in [visited_location_id, location_id]:
            if id <= 0 or id == '':
                raise BadRequestErrors

        return self._animals_dao.replace_location_on_animal(visited_location_id=visited_location_id,
                                                            location_id=location_id,
                                                            animal_id=animal_id)


# =====================ANIMALS TYPES SERVICE =============================================
# .
class AnimalsTypesService(BaseService):
    def __init__(self, db_session) -> None:
        super().__init__(db_session)
        self._animals_types_dao = AnimalsTypesDAO(db_session)

    @staticmethod
    def serialize_type(type_: TypeAnimals):
        return {
            'id': type_.id,
            'type': type_.type
        }

    def get_item(self, animals_types_id: int) -> dict[str, Any]:
        return self.serialize_type(
            self._animals_types_dao.get_by_id(animals_types_id))

    def add_new_animals_types(self, **kwargs):

        if ((type_ := kwargs.get('type')) == '') or type_ is None:
            raise BadRequestErrors

        return self.serialize_type(
            self._animals_types_dao.add_new_animals_types(type=type_))

    def update_animals_types(self, longitude_id: int, **kwargs):

        if len(type := kwargs.get('type')) <= 0 or type == '':
            raise BadRequestErrors

        return self.serialize_type(
            self._animals_types_dao.update_animals_types(longitude_id, type=type))

    def delete_animals_types(self, user_id: int) -> None:
        self._animals_types_dao.remove_animals_types(user_id)
