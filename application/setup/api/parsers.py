from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser
# .
# =====================CREATE API PARSERS WHICH WILL SERIALIZE DATA INTO USER===========================================

registration_parser: RequestParser = RequestParser()
registration_parser.add_argument(name='email', type=email(), required=True, nullable=False)
registration_parser.add_argument(name='password', type=str, required=True, nullable=False)
registration_parser.add_argument(name='firstName', type=str, nullable=False)
registration_parser.add_argument(name='lastName', type=str, nullable=False)


auth_parser: RequestParser = RequestParser()
auth_parser.add_argument(name='email', type=email(), required=True, nullable=False)
auth_parser.add_argument(name='password', type=str, required=True, nullable=False)


locations_parser: RequestParser = RequestParser()
locations_parser.add_argument(name='latitude', type=int, required=True, nullable=False)
locations_parser.add_argument(name='longitude', type=int, required=True, nullable=False)


change_password_parser: RequestParser = RequestParser()
change_password_parser.add_argument(name='name', type=str, required=True)
change_password_parser.add_argument(name='surname', type=str, required=True)

page_parser: RequestParser = RequestParser()
page_parser.add_argument(name='page', type=int, location='args', required=True)

tokens_parser: RequestParser = RequestParser()
tokens_parser.add_argument(name='access_token', type=str, required=True)
tokens_parser.add_argument(name='refresh_token', type=str, required=True)

animals_types_parser: RequestParser = RequestParser()
animals_types_parser.add_argument(name='type', type=str, required=True)

animals_parser: RequestParser = RequestParser()
animals_parser.add_argument(name='animalTypes', type=list, required=True)
animals_parser.add_argument(name='weight', type=float, required=True)
animals_parser.add_argument(name='length', type=float, required=True)
animals_parser.add_argument(name='height', type=float, required=True)
animals_parser.add_argument(name='gender', type=str, required=True)
animals_parser.add_argument(name='chipperId', type=int, required=True)
animals_parser.add_argument(name='chippingLocationId', type=int, required=True)




