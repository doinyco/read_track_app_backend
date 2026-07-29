def test_app_is_created(app):
    assert app is not None
    assert app.testing is True

def test_unknown_route_returns_404(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404