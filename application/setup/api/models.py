from flask_restx import fields, Model

from application.setup.api import api
# .
# =====================CREATE MODELS IN API =============================================

error: Model = api.model('Сообщение об ошибке', {
    'message': fields.String(required=True, example=1),
    'errors': fields.Wildcard(fields.String(), required=False)
})

user_profile = api.model('Профиль пользователя', {
    'id': fields.Integer(required=True),
    'email': fields.String(required=True),
    'name': fields.String,
    'surname': fields.String
})

tokens = api.model('Accesss and Refresh tokens', {
    'access_token': fields.String(required=True),
    'refresh_token': fields.String(required=True),
})