from flask import Flask
from .db import db
import os
from flask_cors import CORS
from .db import migrate

def create_app():
    print("Testing Deployment and deployments is successful if this prints")
    
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    if config:
        app.config.update(config)

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints here
    # app.register_blueprint()

    # Enable CORS
    CORS(app)

    return app