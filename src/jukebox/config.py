import os

class BaseConfig(object):
    DEBUG = False
    TESTING = False

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

    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '99aa66a4fbf04bb097f6c1b4801cecbc')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', 'c7109ecb0e7d4a6c999634a16fe13150')

    SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME', '113566434')
    SPOTIFY_SOURCE_PLAYLIST_URI = os.environ.get('SPOTIFY_SOURCE_PLAYLIST_URI', '44x9Ip9p7A9Po4nXVgiPsZ')
    SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost/')

    SCOPE = 'playlist-modify-public playlist-modify-private'

class DevConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True
    TESTING = False


class TestConfig(BaseConfig):
    ENV = 'test'
    DEBUG = False
    TESTING = True


class ProdConfig(DevConfig):
    ENV = 'prod'
    DEBUG = False
    TESTING = False

    # POSTGRES
    POSTGRES = {
        'user': os.environ.get('POSTGRES_USER'),
        'pw': os.environ.get('POSTGRES_PASSWORD'),
        'db': 'postgres',
        'host': 'borrel_database',
        'port': '5432',
    }

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES