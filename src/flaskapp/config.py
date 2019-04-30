import os
from dotenv import load_dotenv

class BaseConfig(object):
    load_dotenv()

    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY')

    BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
    BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')

    # POSTGRES
    POSTGRES = {
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'pw': os.environ.get('POSTGRES_PASSWORD', 'docker'),
        'db': 'postgres',
        'host': 'localhost',
        'port': '5432',
    }

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    ENV = 'test'
    DEBUG = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../db/test.db'

class DevConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True
    TESTING = False


class ProdConfig(DevConfig):
    ENV = 'prod'
    DEBUG = False
    TESTING = False
