from flask import Flask
from src.flaskapp.views.main.main import main
from src.flaskapp.views.vote.vote import vote
from src.flaskapp.views.error.error import error
from .extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('.secrets')

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(vote)
    app.register_blueprint(error)

    with app.app_context():
        db.Model.metadata.reflect(db.engine)

    return app
