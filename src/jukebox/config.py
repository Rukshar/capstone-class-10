import os
from dotenv import load_dotenv

class BaseConfig(object):
    load_dotenv()

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

    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

    # Spotify
    SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USERNAME')
    SPOTIFY_SOURCE_PLAYLIST_URI = os.environ.get('SPOTIFY_SOURCE_PLAYLIST_URI')
    SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

    SCOPE = 'playlist-modify-public playlist-modify-private'
    CACHE_PATH = './cache/cache-{}'.format(os.environ.get('SPOTIFY_USERNAME'))

class DevConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True
    TESTING = False


class TestConfig(BaseConfig):
    ENV = 'test'
    DEBUG = False
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///src/db/test.db'

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

    # Spotify
    CACHE_PATH = '/cache/cache-{}'.format(os.environ.get('SPOTIFY_USERNAME'))