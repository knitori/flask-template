
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config) -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile(config)

    db.init_app(app)
    login_manager.init_app(app)

    # simple csrf protection
    from . import csrf
    app.before_request(csrf.csrf_protect)
    app.jinja_env.globals['csrf_token'] = csrf.generate_csrf_token

    # ensure some imports
    from .src import models

    @login_manager.user_loader
    def find_user(user_id):
        # probably shouldn't be a closure
        return models.User.query.find_by(id=int(user_id)).first()

    register_blueprints(app)

    return app


def register_blueprints(app: Flask):
    from .src.views import (
        main
    )
    app.register_blueprint(main)
