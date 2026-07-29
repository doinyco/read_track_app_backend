import os
import pytest
from app import create_app
from app.db import db as _db

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/bookapp_test",
)

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URL,
    })
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()