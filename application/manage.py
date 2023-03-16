import logging

from flask import Flask
from flask_cors import CORS

from application.config import Config
from application.errors import BaseProjectException
from application.setup.api import api
from application.setup.db import db
from application.views import auth_ns
from application.views.main.accounts import accounts_ns
from application.views.main.animals import animals_ns
from application.views.main.locations import locations_ns


# ================# .================MAIN FILE TO CONSTRUCT FLASK API================================================

def create_app(config_object: str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.logger.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)

    CORS(app=app)

    db.init_app(app)
    api.init_app(app)

    api.add_namespace(auth_ns)
    api.add_namespace(accounts_ns)
    api.add_namespace(locations_ns)
    api.add_namespace(animals_ns)

    app.app_context().push()

    @api.errorhandler(BaseProjectException)
    def handle_validation_error(error: BaseProjectException):
        return {'message': error.message}, error.code

    return app


if __name__ == '__main__':
    app = create_app(Config())
    db.create_all()
    app.run()
