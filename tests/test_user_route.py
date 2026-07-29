from app.models.user import User

def test_register_creates_user(client, app):
    response = client.post("/users/register", json={
        "email": "abc@example.com",
        "username": "abc",
        "password": "correct-horse-battery-staple",
    })
    
    assert response.status_code == 201
    assert response.get_json() == {"message": "User registered"}
    
    with app.app_context():
        user = User.query.filter_by(username="abc").first()
        assert user is not None
        assert user.email == "abc@example.com"
        assert user.password_hash != "correct-horse-battery-staple"