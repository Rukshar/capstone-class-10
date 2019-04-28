import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False


    SQLALCHEMY_DATABASE_URI = 'sqlite:///../db/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key') #TODO Change me


class DevelopmentConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True

class ProdConfig(DevelopmentConfig):
    ENV = 'prod'
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # POSTGRES
    POSTGRES = {
        'user': os.environ.get('POSTGRES_USER'),
        'pw': os.environ.get('POSTGRES_PASSWORD'),
        'db': 'postgres',
        'host': 'localhost',
        'port': '5432',
    }

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_TRACK_MODIFICATIONS = False