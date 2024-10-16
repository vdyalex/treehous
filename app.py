from dynaconf import FlaskDynaconf
from flask import Flask

from api.models import db
from api.interceptors import jwt


from config import settings


def create_app(**config):
    app = Flask(__name__)
    FlaskDynaconf(app, dynaconf_instance=settings, **config)

    app.secret_key = app.config["APP_SECRET_KEY"]

    # NOT RECOMMENDED IN PRODUCTION - DISABLED SINCE THIS IS A PROJECT SAMPLE
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    db.init_app(app)
    jwt.init_app(app)

    from api.routes.root import blueprint as root
    from api.routes.auth import blueprint as auth
    from api.routes.user import blueprint as user

    app.register_blueprint(root)
    app.register_blueprint(auth)
    app.register_blueprint(user)

    @app.before_request
    def database_create_tables():
        app.before_request_funcs[None].remove(database_create_tables)
        db.create_all()

    return app
