from flask_restx import Resource, Namespace
from flask import request

from application.errors import BadRequestErrors, AuthenticationErrors
from application.service import AuthService
from application.service.main.animals import AnimalsTypesService, AnimalsService
from application.setup.api.parsers import animals_types_parser, animals_parser
from application.setup.db import db
from application.setup.api.models import error
from application.utils.security import check_user, compare_passwords
from application.utils.useful_features import check_id, check_on_space

animals_ns = Namespace('animals')


# ==============ANIMALS========================================


@animals_ns.route('/')
class AnimalsView(Resource):

    @animals_ns.expect(animals_parser)
    def post(self):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        new_animal = AnimalsService(db.session).add_new_animals(**request.get_json())

        add_location = AnimalsService(db.session).add_new_locations(new_animal.get('id'),
                                                                    location_id=new_animal.get('chippingLocationId'))

        return add_location, 201


@animals_ns.route('/<string:animal_id>')
class AnimalsView(Resource):

    @staticmethod
    def get(animal_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        animal = AnimalsService(db.session).get_item(animal_id)

        return animal, 200

    @staticmethod
    @animals_ns.expect(animals_parser)
    def put(animal_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        update_animal = AnimalsService(db.session).update_animals(animal_id, **request.get_json())

        return update_animal, 200

    @staticmethod
    def delete(animal_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        AnimalsService(db.session).delete_animals(animal_id)

        return None, 200


@animals_ns.route('/search')
class AnimalsView(Resource):

    @staticmethod
    def get():

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animals = AnimalsService(db.session).search_animals()

        return animals


"""
- response
Body {
    "id": "long",				// Идентификатор животного
    "animalTypes": "[long]",		// Массив идентификаторов типов животного
    "weight": "float",			// Масса животного, кг
    "length": "float",			// Длина животного, м
    "height": "float",			// Высота животного, м
    "gender": "string", 			// Гендерный признак животного, доступные значения “MALE”, “FEMALE”, “OTHER”
    "lifeStatus": "string", 			// Жизненный статус животного, доступные значения “ALIVE”(устанавливается 
        автоматически при добавлении нового животного), “DEAD”(можно установить при обновлении информации о животном)
    "chippingDateTime": "dateTime", 	// Дата и время чипирования в формате ISO-8601 (устанавливается автоматически 
        на момент добавления животного)
    "chipperId": "int",			// Идентификатор аккаунта пользователя, чипировавшего животное
    "chippingLocationId": "long",		// Идентификатор точки локации животных
	"visitedLocations": "[long]", 		// Массив идентификаторов объектов с информацией о посещенных точках локаций
    "deathDateTime": "dateTime"		// Дата и время смерти животного в формате ISO-8601 
    (устанавливается автоматически при смене lifeStatus на “DEAD”). Равняется null, пока lifeStatus = “ALIVE”.)
 }
"""


# ==============LOCATIONS========================================

@animals_ns.route('/<string:animal_id>/locations/<string:point_id>')
class AnimalsView(Resource):

    @staticmethod
    def post(animal_id, point_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)
        point_id = check_id(point_id)

        update_animal = AnimalsService(db.session).update_location_on_animals(animal_id, point_id)
        AnimalsService(db.session).update_time_location_on_animal(animal_id)

        return update_animal, 201

    @staticmethod
    def delete(animal_id, point_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)
        point_id = check_id(point_id)

        AnimalsService(db.session).delete_location_on_animals(animal_id, point_id)

        return None, 200


@animals_ns.route('/<string:animal_id>/locations/')
class AnimalsView(Resource):

    def put(self, animal_id: str):

        print(f'CHECK')

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        update_animal = AnimalsService(db.session).replace_location_on_animal(animal_id=animal_id, **request.get_json())

        return update_animal, 200


@animals_ns.route('/<string:animal_id>/locations')
class AnimalsView(Resource):
    @staticmethod
    def get(animal_id: str):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        locations = AnimalsService(db.session).search_locations_on_animals(animal_id=animal_id, **request.get_json())

        return locations, 200


# ==============TYPES========================================


@animals_ns.route('/<string:animal_id>/types/')
class AnimalsView(Resource):
    @staticmethod
    def put(animal_id: str):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)

        update_animal = AnimalsService(db.session).replace_type_on_animals(animal_id=animal_id, **request.get_json())

        return update_animal, 200


@animals_ns.route('/types')
class AnimalsTypesView(Resource):

    @animals_ns.expect(animals_types_parser)
    @animals_ns.response(code=400, description='Bad request', model=error)
    def post(self):

        """
                - request
        Body {
            "type": "string"		// Тип животного						}

                - response
        Body {
            "id": "long",		// Идентификатор типа животного
            "type": "string"		// Тип животного
        }

        :return: TYPES
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        types = AnimalsTypesService(db.session).add_new_animals_types(**animals_types_parser.parse_args())

        return types, 201


@animals_ns.route('/types/<string:animals_types_id>/')
class AnimalsTypesView(Resource):

    @animals_ns.response(code=400, description='Bad request', model=error)
    def get(self, animals_types_id):

        """ - request
            Body {
                empty
            }

                - response
            Body {
                "id": "long", 		// Идентификатор типа животного
                "type": "string" 	// Тип животного
                 }
            """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animals_types_id = check_id(animals_types_id)

        types = AnimalsTypesService(db.session).get_item(animals_types_id)

        return types, 200

    @animals_ns.expect(animals_types_parser)
    def put(self, animals_types_id):

        """
                - request
        Body {
            "type": "string"		// Новый тип животного
        }

                - response
        Body {
            "id": "long",		// Идентификатор типа животного
            "type": "string"		// Новый тип животного
        }

        :param animals_types_id:
        :return: TYPES
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        if not check_on_space(request.get_json()):
            raise BadRequestErrors

        types = AnimalsTypesService(db.session).update_animals_types(animals_types_id,
                                                                     **animals_types_parser.parse_args())

        return types, 200

    @animals_ns.response(code=200, description='Success')
    @animals_ns.response(code=400, description='Bad reqeust', model=error)
    @animals_ns.response(code=401, description='Request from Not Authorisation User', model=error)
    @animals_ns.response(code=403, description='This accounts not found or you haven"t rights', model=error)
    def delete(self, animals_types_id):

        """
                - request
        Body {
            empty
        }

                - response
        Body {
            empty
        }
        """

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animals_types_id = check_id(animals_types_id)

        AnimalsTypesService(db.session).delete_animals_types(animals_types_id)

        return None, 200


@animals_ns.route('/<string:animal_id>/types/<string:type_id>/')
class AnimalsView(Resource):

    @staticmethod
    def post(animal_id, type_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)
        type_id = check_id(type_id)

        update_animal = AnimalsService(db.session).update_type_on_animals(animal_id, type_id)

        return update_animal, 201

    @staticmethod
    def delete(animal_id, type_id):

        if not request.headers.get('Authorization'):
            raise AuthenticationErrors

        identified_user = check_user(request.headers.get('Authorization'))

        if not ((current_user := AuthService(db.session).get_user_by_email(**identified_user)) and compare_passwords(
                current_user.password, identified_user.get('password'))):
            raise AuthenticationErrors

        animal_id = check_id(animal_id)
        type_id = check_id(type_id)

        update_animal = AnimalsService(db.session).delete_type_on_animals(animal_id, type_id)

        return update_animal, 200
