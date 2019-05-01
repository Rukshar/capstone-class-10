import sys
sys.path.append("../")

from flask import Flask
from src.flaskapp.views.main.main import main
from src.flaskapp.views.vote.vote import vote
from src.flaskapp.views.error.error import error
from src.flaskapp.views.admin.admin import admin
from src.flaskapp.views.dashboard.dashboard import dashboard
from src.flaskapp.extensions import db
from src.flaskapp.extensions import basic_auth
from src.flaskapp.config import *
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)

    env = os.environ.get('ENV')
    if env is None:
        app.logging.error('No environment specified')
        raise Exception('No environment specified')

    if env == 'prod':
        config = ProdConfig
    elif env == 'test':
        config = TestConfig
    elif env == 'dev':
        config = DevConfig
    else:
        app.logging.error('No configuration loaded')
        raise Exception('Configuration not loaded')

    app.config.from_object(config)

    db.init_app(app)
    basic_auth.init_app(app)

    with app.app_context():
        db.create_all()
        db.Model.metadata.reflect(db.engine)

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(vote)
    app.register_blueprint(error)
    app.register_blueprint(admin)
    app.register_blueprint(dashboard)
