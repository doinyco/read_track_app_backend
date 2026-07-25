import os
import requests
from flask import Flask
from dotenv import load_dotenv
from .db import db, migrate
from .models import book, progress, reading_list, user # noqa: F401 -- registers models with Base.metadata for migrations

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_pre_ping": True, # recycles dead connections--this helps handle failover/idle timeout on RDS
    "pool_recycle": 300,
}

db.init_app(app)
migrate.init_app(app, db)

NYT_BOOKS_API_KEY = os.getenv("NYT_BOOKS_API_KEY")

@app.route("/")
def hello_world():
    response = requests.get(
        "https://api.nytimes.com/svc/books/v3/lists/overview.json",
        params={"api-key": NYT_BOOKS_API_KEY},
    )
    
    return response.json()