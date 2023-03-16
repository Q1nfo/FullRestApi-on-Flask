from typing import List, Optional, Any, Type, Dict

from datetime import datetime

from timedelta_isoformat import timedelta as td

from flask_restx.inputs import datetime_from_iso8601
from sqlalchemy.orm import RelationshipProperty

from application.setup.db import db

from flask import abort, request
from flask_sqlalchemy import BaseQuery
from sqlalchemy import desc, asc, and_
from sqlalchemy.exc import IntegrityError

from application.dao.base import BaseDAO
from application.errors import BadRequestErrors, ConflictError, NotFoundErrors
from application.models import TypeAnimals, Animal, Location, User, LocationTime


class AnimalsDAO(BaseDAO[Animal]):
    __model__ = Animal

    # =====================FUNC TO UPDATE SOME DATA IN ANIMALS =============================================

    def update_time_location_on_animal(self, animal_id):
        animal = self.get_by_id(animal_id)
        animal.chippingDatetime = datetime.now()
        self.db_session.add(animal)
        self.db_session.commit()

    def get_by_id_new(self, pk: int):
        return self._create_data(
            self.db_session.query(self.__model__).get_or_404(pk))

    def _delete_types(self, animal):
        animal.type_animals.clear()
        self.db_session.add(animal)
        self.db_session.commit()

    def _remove_animals_on_location(self, location, animal):
        location.animals.remove(animal)
        self.db_session.add(location)
        self.db_session.commit()

    def _delete_locations(self, animal):
        animal.visited_locations.clear()
        self.db_session.add(animal)
        self.db_session.commit()

    # =====================FUNC TO HEAD ENDPOINTS IN ANIMALS =============================================

    @staticmethod
    def _create_data(obj: Animal) -> dict[str, str | datetime | int | Any]:
        death_date_time = None if obj.lifeStatus == 'ALIVE' else datetime.now().isoformat()
        type_animal = [x.id for x in obj.type_animals]
        visited_location = [x.id for x in obj.visited_locations]
        chippingDateTime = obj.chippingDatetime.isoformat()
        deathDateTime = death_date_time
        data = {
            'id': obj.id,
            'animalTypes': type_animal,
            'weight': obj.weight,
            'length': obj.length,
            'height': obj.height,
            'gender': obj.gender,
            'lifeStatus': obj.lifeStatus,
            'chippingDateTime': chippingDateTime,
            'chipperId': obj.chipperId,
            'chippingLocationId': obj.chippingLocationId,
            'visitedLocations': visited_location,
            'deathDateTime': deathDateTime
        }

        return data

    def add_new_animals(self, **kwargs) -> dict[str, str | datetime | int | Any]:

        animal_types = kwargs.get('animalTypes')
        weight = kwargs.get('weight')
        length = kwargs.get('length')
        height = kwargs.get('height')
        gender = kwargs.get('gender')
        life_status = 'ALIVE'
        chipper_id = kwargs.get('chipperId')
        chipping_location_id = kwargs.get('chippingLocationId')

        for type_ in animal_types:
            if not self.db_session.query(TypeAnimals).filter(TypeAnimals.id == type_).first():
                raise NotFoundErrors

        if not self.db_session.query(User).filter(User.id == chipper_id).first():
            raise NotFoundErrors

        if not self.db_session.query(Location).filter(Location.id == chipping_location_id).first():
            raise NotFoundErrors

        if len(animal_types) != len(list(set(animal_types))):
            raise ConflictError

        obj = Animal(weight=weight,
                     length=length,
                     height=height,
                     gender=gender,
                     lifeStatus=life_status,
                     chippingDatetime=datetime.now(),
                     chipperId=chipper_id,
                     chippingLocationId=chipping_location_id)

        try:
            self.db_session.add(obj)
            self.db_session.commit()
        except IntegrityError:
            raise ConflictError('User with this email already exists.')

        animal = self.db_session.query(Animal).filter(Animal.id == obj.id).first()

        location_time = LocationTime(animal_id=animal.id,
                                     location_id=animal.chippingLocationId,
                                     startDateTime=datetime.now())

        self.db_session.add(location_time)
        self.db_session.commit()

        types = []

        for type in animal_types:
            types.append(self.db_session.query(TypeAnimals).filter(TypeAnimals.id == type).first())

        animal.type_animals.extend(types)
        db.session.add(animal)
        db.session.commit()

        return self._create_data(animal)

    def add_new_locations(self, animal_id, location_id):

        animal = self.get_by_id(animal_id)
        location = self.db_session.query(Location).filter(Location.id == location_id).first()

        animal.visited_locations.extend([location])
        db.session.commit()

        return self._create_data(animal)

    def update_animals(self, animal_id: int, **kwargs) -> dict:

        new_animal = self.get_by_id(animal_id)

        if kwargs.get('lifeStatus') == 'ALIVE' and new_animal.lifeStatus == 'DEAD':
            raise BadRequestErrors

        if (new_loc := kwargs.get('chippingLocationId')) == new_animal.visited_locations[0].id or kwargs.get(
                'chippingLocationId') == new_animal.visited_locations[-1]:
            raise BadRequestErrors

        if not self.db_session.query(Location).filter(Location.id == new_loc).first():
            raise NotFoundErrors

        if not self.db_session.query(User).filter(User.id == kwargs.get('chipperId')).first():
            raise NotFoundErrors

        old_loc_time = self.db_session.query(LocationTime).filter(
            and_(LocationTime.animal_id == animal_id,
                 LocationTime.location_id == new_animal.chippingLocationId)).first()

        if old_loc_time:
            old_loc_time.endDateTime = datetime.now()

        location_time = LocationTime(animal_id=animal_id,
                                     location_id=new_loc,
                                     startDateTime=datetime.now())

        new_loc = self.db_session.query(Location).filter(Location.id == new_loc).first()

        self._append_location(animal=new_animal, location=new_loc)

        if not new_animal.chipperId == kwargs.get('chipperId'):
            new_animal.chippingDatetime = datetime.now()

        self.db_session.query(Animal).filter(Animal.id == animal_id).update(kwargs)
        self.db_session.add_all([new_animal, location_time])
        self.db_session.commit()

        return self._create_data(new_animal)

    def remove_animals(self, animals_id) -> None:

        if len(self.get_by_id(animals_id).visited_locations) == 1:
            raise BadRequestErrors

        animal = self.get_by_id(animals_id)
        self._delete_types(animal)
        animal = self.get_by_id(animals_id)
        locations = animal.visited_locations
        for location in locations:
            self._remove_location(animal=animal, location=location)

        Animal.query.filter(Animal.id == animals_id).delete()

        # db.session.delete(animal)
        db.session.commit()

    # =====================PRIVATE FUNC TO UPDATE SOME DATA IN ANIMALS =============================================

    def _append_type(self, animal, type):
        animal.type_animals.append(type)
        self.db_session.add(animal)
        self.db_session.commit()

    def _remove_type(self, animal, type):
        animal.type_animals.remove(type)
        self.db_session.add(animal)
        self.db_session.commit()

    def _append_location(self, animal, location):
        animal.visited_locations.append(location)
        self.db_session.add(animal)
        self.db_session.commit()

    def update_type_on_animals(self, animal_id: int, type_id: int):

        if not (animal := self.get_by_id(animal_id)):
            raise NotFoundErrors
        if not (type := self.db_session.query(TypeAnimals).filter(TypeAnimals.id == type_id).first()):
            raise NotFoundErrors

        if type in animal.type_animals:
            raise ConflictError

        self._append_type(animal, type)

        return self._create_data(self.get_by_id(animal_id))

    def delete_type_on_animals(self, animal_id: int, type_id: int):

        if not (animal := self.get_by_id(animal_id)):
            raise NotFoundErrors
        if not (type := self.db_session.query(TypeAnimals).filter(TypeAnimals.id == type_id).first()):
            raise NotFoundErrors
        if type not in animal.type_animals:
            raise NotFoundErrors

        if type in animal.type_animals and len(animal.type_animals) == 1:
            raise BadRequestErrors

        self._remove_type(animal=animal, type=type)

        return self._create_data(self.get_by_id(animal_id))

    def update_location_on_animals(self, animal_id: int, point_id: int):

        if not (animal := self.get_by_id(animal_id)):
            raise NotFoundErrors
        if not (location := self.db_session.query(Location).filter(Location.id == point_id).first()):
            raise NotFoundErrors

        if location == animal.visited_locations[-1]:
            raise BadRequestErrors
        if len(animal.visited_locations) == 1 and location == animal.visited_locations[0]:
            raise BadRequestErrors
        if animal.lifeStatus == 'DEAD':
            raise BadRequestErrors

        self._append_location(animal=animal, location=location)

        animal = self.get_by_id(animal_id)

        return {
            'id': animal.id,
            'dateTimeOfVisitLocationPoint': str(datetime.now() - animal.chippingDatetime),
            'locationPointId': location.id
        }

    def delete_location_on_animals(self, animal_id: int, point_id: int) -> None:

        if not (animal := self.get_by_id(animal_id)):
            raise NotFoundErrors
        if not (location := self.db_session.query(Location).filter(Location.id == point_id).first()):
            raise NotFoundErrors
        if location not in animal.visited_locations:
            raise NotFoundErrors
        if len(animal.visited_locations) not in [0, 1]:
            if location == animal.visited_locations[0]:
                if animal.visited_locations[1] == animal.chippingLocationId:
                    self._remove_location(animal=animal, location=animal.visited_locations[1])
                    self._remove_location(animal=animal, location=location)
                else:
                    self._remove_location(animal=animal, location=location)
            else:
                self._remove_location(animal=animal, location=location)
        else:
            self._remove_location(animal=animal, location=location)

    # =====================FUNC TO SEARCHING IN ANIMALS =============================================

    def search_animals(self, start_date, end_date):

        if request.args.get('size'):
            size = request.args.get('size')
        else:
            size = 10

        if request.args.get('from'):
            from_ = request.args.get('from')
        else:
            from_ = 0

        response = []

        stmt: BaseQuery = self.db_session.query(LocationTime)

        if start_date:
            if end_date:
                locations = stmt.filter(and_(LocationTime.startDateTime >= start_date,
                                             LocationTime.endDateTime <= end_date)).offset(from_).limit(size).all()
            else:
                locations = stmt.filter(and_(LocationTime.startDateTime >= start_date, )).offset(from_).limit(
                    size).all()
        else:
            if end_date:
                locations = stmt.filter(LocationTime.endDateTime <= end_date).limit(size).offset(from_).limit(
                    size).all()
            else:
                locations = stmt.limit(size).offset(from_).limit(size).all()

        locations_double = locations.copy()

        if chipper_id := request.args.get('chipperId'):
            for location in locations:
                if not (animal := self.db_session.query(Animal).filter(Animal.id == location.animal_id).first()):
                    locations_double.remove(location)
                else:
                    if int(animal.chipperId) != int(chipper_id):
                        locations_double.remove(location)

        if chipping_location_id := request.args.get('chippingLocationId'):
            for location in locations:
                if not (animal := self.db_session.query(Animal).filter(Animal.id == location.animal_id).first()):
                    if location in locations_double:
                        locations_double.remove(location)
                else:
                    if int(animal.chippingLocationId) != int(chipping_location_id):
                        if location in locations_double:
                            locations_double.remove(location)

        if life_status := request.args.get('lifeStatus'):
            for location in locations:
                if not (animal := self.db_session.query(Animal).filter(Animal.id == location.animal_id).first()):
                    if location in locations_double:
                        locations_double.remove(location)
                else:
                    if animal.lifeStatus != life_status:
                        if location in locations_double:
                            locations_double.remove(location)

        if gender := request.args.get('gender'):
            for location in locations:
                if not (animal := self.db_session.query(Animal).filter(Animal.id == location.animal_id).first()):
                    if location in locations_double:
                        locations_double.remove(location)
                else:
                    if animal.gender != gender:
                        if location in locations_double:
                            locations_double.remove(location)

        for location in locations_double:
            if not location.endDateTime:
                date_time = datetime.now() - location.startDateTime
            else:
                date_time = location.endDateTime - location.startDateTime
            response.append({
                'id': location.animal_id,
                'dateTimeOfVisitLocationPoint': str(date_time),
                'locationPointId': location.location_id
            })

        response_double = response.copy()

        for resp in response:
            if not self.db_session.query(Animal).filter(Animal.id == (resp['id'])).first():
                response_double.remove(resp)

        return response_double

    def replace_type_on_animals(self, animal_id: int, oid: int, nid: int):

        animal = self.get_by_id(animal_id)

        if False in [old_type := self.db_session.query(TypeAnimals).filter(TypeAnimals.id == oid).first(),
                     new_type := self.db_session.query(TypeAnimals).filter(TypeAnimals.id == nid).first()]:
            raise NotFoundErrors

        if old_type not in animal.type_animals:
            raise NotFoundErrors

        if new_type in animal.type_animals:
            raise ConflictError

        if old_type and new_type in animal.type_animals:
            raise ConflictError

        self._remove_type(animal=animal, type=old_type)
        self._append_type(animal=animal, type=new_type)

        return self._create_data(self.get_by_id(animal_id))

    def search_locations_on_animals(self, animal_id: int, start_date, end_date, **kwargs):

        if request.args.get('size'):
            size = request.args.get('size')
        else:
            size = 10

        if request.args.get('from'):
            from_ = request.args.get('from')
        else:
            from_ = 0

        animal = self.get_by_id(animal_id)

        response = []

        stmt: BaseQuery = self.db_session.query(LocationTime)

        if start_date:
            if end_date:
                locations = stmt.filter(and_(LocationTime.animal_id == animal_id,
                                             LocationTime.startDateTime >= start_date,
                                             LocationTime.endDateTime <= end_date)).offset(from_).limit(size).all()
            else:
                locations = stmt.filter(and_(LocationTime.animal_id == animal_id,
                                             LocationTime.startDateTime >= start_date, )).offset(from_).limit(
                    size).all()
        else:
            if end_date:
                locations = stmt.filter(and_(LocationTime.animal_id == animal_id,
                                             LocationTime.endDateTime <= end_date)).limit(size).offset(from_).limit(
                    size).all()
            else:
                locations = stmt.filter(LocationTime.animal_id == animal_id).limit(size).offset(from_).limit(size).all()

        for location in locations:
            if not location.endDateTime:
                break
            date_time = location.endDateTime - location.startDateTime
            response.append({
                'id': animal_id,
                'dateTimeOfVisitLocationPoint': str(date_time),
                'locationPointId': location.location_id
            })
        return response

    def _remove_location(self, animal, location):
        animal.visited_locations.remove(location)
        self.db_session.add(animal)
        self.db_session.commit()

    def replace_location_on_animal(self, animal_id: int, visited_location_id: int, location_id: int):

        animal = self.get_by_id(animal_id)

        visited_location = self.db_session.query(Location).filter(Location.id == visited_location_id).first()

        location = self.db_session.query(Location).filter(Location.id == location_id).first()

        if location:
            raise NotFoundErrors

        if visited_location:
            raise NotFoundErrors

        if location.id == animal.chippingLocationId or location in animal.visited_locations:
            raise BadRequestErrors

        if visited_location == location:
            raise BadRequestErrors

        if visited_location not in animal.visited_locations:
            raise NotFoundErrors

        self._remove_location(animal=animal, location=visited_location)
        self._append_location(animal=animal, location=location)

        return {
            'id': animal_id,
            'dateTimeOfVisitLocationPoint': str(datetime.now() - animal.chippingDatetime),
            'locationPointId': location_id
        }


# =====================FUNC IN ANIMALS TYPES =============================================
class AnimalsTypesDAO(BaseDAO[TypeAnimals]):
    __model__ = TypeAnimals

    def add_new_animals_types(self, type) -> TypeAnimals:

        if self.db_session.query(TypeAnimals).filter(TypeAnimals.type == type).all():
            raise ConflictError

        print(type)
        obj = TypeAnimals(type=type)
        try:
            self.db_session.add(obj)
            self.db_session.commit()
        except Exception():
            raise BadRequestErrors

        return obj

    def update_animals_types(self, animals_types_id: int, type: str) -> TypeAnimals:

        if self.db_session.query(TypeAnimals).filter(TypeAnimals.type == type).all():
            raise ConflictError

        old_type = self.get_by_id(animals_types_id)
        old_type.type = type
        self.db_session.commit()

        return self.get_by_id(animals_types_id)

    def remove_animals_types(self, animals_types_id: int) -> None:

        type_ = self.get_by_id(animals_types_id)

        if type_.animals:
            raise BadRequestErrors

        self.db_session.delete(type_)
        self.db_session.commit()

# .
