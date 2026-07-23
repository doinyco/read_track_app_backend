from flask import Flask
from .routes.user_route import user_bp


def create_app():

    app = Flask(__name__)

    app.register_blueprint(
        user_bp,
        url_prefix="/auth"
    )

    return app