import base64
import os
from enum import Enum
from typing import List

# ===========# .=====================MAIN CONFIG FILE ================================================

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess')
    ITEM_PER_PAGE: int = 12
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRE_MINUTES = 15
    TOKEN_EXPIRE_DAYS = 150

    BUNDLE_ERRORS = True

    PWD_HASH_SALT: bytes = base64.b64decode(os.getenv('HASH_SALT', 'salt'))
    PWD_HASH_ITERATIONS: int = 100_000

    RESTX_ERROR_404_HELP = False
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    RESTX_JSON = {
        'ensure_ascii': False ,
    }

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, '../test.db')
    """SLITE DB"""
    # SQLALCHEMY_DATABASE_URI = os.getenv('SPRING_DATASOURCE_URL')
    """POSTGRE DB"""
    SWAGGER_SUPPORTED_SUBMIT_METHODS: List[str] = []


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ITEMS_PER_PAGE: int = 3
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, '../test.db')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SPRING_DATASOURCE_URL')
    SWAGGER_SUPPORTED_SUBMIT_METHODS: List[str] = []


class Config(Enum):
    development = DevelopmentConfig
    testing = TestingConfig
    production = ProductionConfig


def get_config(config_name: str):
    return getattr(Config, config_name, Config.production).value
