import sys
sys.path.append("../")

from flask import Flask
from src.flaskapp.views.main.main import main
from src.flaskapp.views.vote.vote import vote
from src.flaskapp.views.error.error import error
from src.flaskapp.views.admin.admin import admin
from src.flaskapp.extensions import db
from src.flaskapp.extensions import basic_auth
from src.flaskapp.config import *


def create_app(ConfigObject=DevelopmentConfig):

    env = os.environ.get('ENV')

    if ConfigObject:
        config = ConfigObject
    else:
        if env == 'production':
            config = ProdConfig
        elif env == 'testing':
            config = TestingConfig
        else:
            config = DevelopmentConfig

    app = Flask(__name__)
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
