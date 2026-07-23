import os
import requests
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NYT_BOOKS_API_KEY = os.getenv("NYT_BOOKS_API_KEY")

@app.route("/")
def hello_world():
    response = requests.get(
        "https://api.nytimes.com/svc/books/v3/lists/overview.json",
        params={"api-key": NYT_BOOKS_API_KEY},
    )
    
    return response.json()