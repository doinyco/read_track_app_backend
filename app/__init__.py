import os

from flask import Flask
from flask.cli import load_dotenv
from flask_cors import CORS
from .db import migrate
from app.routes import reading_list_routes

from .db import db, migrate
from .models import book, progress, reading_list, user # noqa: F401 -- registers models with Base.metadata for migrations
from .routes.main import main_bp
from .routes.user_route import user_bp
from .routes.dashboard_route import dashboard_bp

# Load environment variables from a .env file if it exists
load_dotenv()

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
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints here
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reading_list_routes.bp)
    app.register_blueprint(dashboard_bp)

    # Enable CORS
    CORS(app,
         supports_credentials=True,
        origins=["http://localhost:5173"])

    return app