import os

import requests
from flask import Blueprint

main_bp = Blueprint("main", __name__)

NYT_BOOKS_API_KEY = os.getenv("NYT_BOOKS_API_KEY")

@main_bp.route("/")
def hello_world():
    response = requests.get(
        "https://api.nytimes.com/svc/books/v3/lists/overview.json",
        params={"api-key": NYT_BOOKS_API_KEY},
    )
    return response.json()