import os

from flask import Flask
from flask_cors import CORS

from .db import db, migrate
from .models import book, progress, reading_list, user # noqa: F401 -- registers models with Base.metadata for migrations
from .routes.main import main_bp

def create_app(config=None):
    app = Flask(__name__)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True, # recycles dead connections--this helps handle failover/idle timeout on RDS
        "pool_recycle": 300,
    }
    
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    app.register_blueprint(main_bp)

    return app